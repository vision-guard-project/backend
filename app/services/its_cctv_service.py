import requests
from flask import current_app
from app.repositories import cctv_repository


def sync_its_cctvs():
    """
    ITS API에서 CCTV 목록을 받아온 뒤,
    서울/경기권 CCTV 2대만 MVP용으로 DB에 저장한다.

    중요:
    ITS CCTV API는 apiKey, type, cctvType, minX, maxX, minY, maxY, getType 같은
    좌표 기반 필수 파라미터가 빠지면 4002 필수 파라미터 오류가 발생한다.
    """

    api_url = current_app.config["ITS_CCTV_API_URL"]
    api_key = current_app.config["ITS_API_KEY"]

    if not api_key:
        raise ValueError("ITS_API_KEY가 설정되지 않았습니다. .env를 확인해주세요.")

    params = {
        "apiKey": api_key,

        # all은 환경에 따라 오류가 날 수 있어서, 우선 its로 요청한다.
        # 필요 시 ex / its를 각각 시도하도록 아래에서 fallback 처리한다.
        "type": "its",

        # 1: 실시간 CCTV
        "cctvType": 1,

        # 서울/경기권 대략 범위
        # X = 경도, Y = 위도
        "minX": 126.70,
        "maxX": 127.35,
        "minY": 37.20,
        "maxY": 37.85,

        "getType": "json",
    }

    data = _request_its_cctv(api_url, params)

    raw_items = _extract_items(data)

    # its 타입에서 결과가 없으면 ex 타입도 한 번 더 시도한다.
    if not raw_items:
        fallback_params = {
            **params,
            "type": "ex",
        }
        data = _request_its_cctv(api_url, fallback_params)
        raw_items = _extract_items(data)

    if not raw_items:
        raise ValueError("ITS CCTV 응답에서 CCTV 목록을 찾지 못했습니다.")

    selected = []
    seoul_added = False
    gyeonggi_added = False

    for item in raw_items:
        parsed = _parse_cctv_item(item)

        if not parsed["streamUrl"]:
            continue

        name = parsed["name"]
        address_text = parsed["address"]

        if not seoul_added and _is_seoul(name, address_text):
            parsed["region"] = "서울"
            selected.append(parsed)
            seoul_added = True

        elif not gyeonggi_added and _is_gyeonggi(name, address_text):
            parsed["region"] = "경기"
            selected.append(parsed)
            gyeonggi_added = True

        if len(selected) >= 2:
            break

    # 서울/경기 필터가 실패했을 경우에도 MVP 화면 테스트를 위해 앞 2대 사용
    if len(selected) < 2:
        selected = []

        for item in raw_items:
            parsed = _parse_cctv_item(item)

            if not parsed["streamUrl"]:
                continue

            parsed["region"] = "테스트"
            selected.append(parsed)

            if len(selected) >= 2:
                break

    if not selected:
        raise ValueError("사용 가능한 CCTV 스트림 URL을 찾지 못했습니다.")

    saved = cctv_repository.replace_two_cctvs(selected)
    return [c.to_dict() for c in saved]


def get_cctvs():
    """
    DB에 CCTV가 있으면 DB 기준으로 반환하고,
    없으면 ITS API에서 동기화한다.
    """

    cctvs = cctv_repository.find_all()

    if not cctvs:
        return sync_its_cctvs()

    return [c.to_dict() for c in cctvs]


def start_cctv(cctv_id):
    """
    CCTV 동작 처리.

    실제 스트리밍 서버를 띄우는 구조가 아니라,
    MVP 단계에서는 DB의 is_running 상태를 True로 바꾸고
    프론트가 재생할 streamUrl을 반환한다.
    """

    cctv = cctv_repository.find_by_id(cctv_id)

    if not cctv:
        raise ValueError("CCTV를 찾을 수 없습니다.")

    cctv.is_running = True
    cctv_repository.save(cctv)

    return {
        "cctvId": str(cctv.id),
        "isRunning": True,
        "streamUrl": cctv.stream_url,
        "message": "CCTV 동작 시작",
    }


def stop_cctv(cctv_id):
    """
    CCTV 종료 처리.

    MVP 단계에서는 DB 상태만 False로 변경한다.
    프론트에서는 이 응답을 받으면 video 영역을 정지 상태 UI로 바꾸면 된다.
    """

    cctv = cctv_repository.find_by_id(cctv_id)

    if not cctv:
        raise ValueError("CCTV를 찾을 수 없습니다.")

    cctv.is_running = False
    cctv_repository.save(cctv)

    return {
        "cctvId": str(cctv.id),
        "isRunning": False,
        "streamUrl": None,
        "message": "CCTV 종료",
    }


def get_snapshot(cctv_id, seconds_ago=30):
    """
    30초 전 화면 조회.

    정확한 30초 전 화면을 구현하려면:
    1. OpenCV로 프레임을 계속 읽고
    2. deque 같은 버퍼에 최근 30초 프레임을 저장하고
    3. 요청 시 해당 시점 프레임을 이미지로 내려줘야 한다.

    지금 MVP에서는 프론트 연결 확인용으로 현재 streamUrl을 snapshotUrl로 반환한다.
    """

    cctv = cctv_repository.find_by_id(cctv_id)

    if not cctv:
        raise ValueError("CCTV를 찾을 수 없습니다.")

    return {
        "cctvId": str(cctv.id),
        "snapshotUrl": cctv.stream_url,
        "capturedAt": f"{seconds_ago}초 전 화면 MVP",
    }


def _request_its_cctv(api_url, params):
    """
    ITS CCTV API 요청 공통 함수.

    ITS가 HTTP 200으로 내려와도 header.resultCode 안에
    4002 같은 서비스 오류가 들어올 수 있으므로 별도로 검사한다.
    """

    res = requests.get(api_url, params=params, timeout=10)
    res.raise_for_status()

    data = res.json()

    header = data.get("header") if isinstance(data, dict) else None
    if isinstance(header, dict):
        result_code = str(header.get("resultCode", ""))
        result_msg = header.get("resultMsg", "")

        if result_code and result_code != "0":
            raise ValueError(f"ITS API 오류: {result_code} / {result_msg}")

    return data


def _extract_items(data):
    """
    ITS CCTV API 응답에서 CCTV 목록 배열만 추출한다.

    ITS CCTV API는 보통:
    {
      "response": {
        "data": [
          {...},
          {...}
        ]
      }
    }

    형태로 내려온다.
    """

    if not isinstance(data, dict):
        return []

    # 가장 중요: ITS CCTV API 기본 구조
    response = data.get("response")
    if isinstance(response, dict):
        response_data = response.get("data")

        if isinstance(response_data, list):
            return response_data

        if isinstance(response_data, dict):
            return [response_data]

        body = response.get("body")
        if isinstance(body, dict):
            items = body.get("items")
            if isinstance(items, list):
                return items

            if isinstance(items, dict):
                item = items.get("item")
                if isinstance(item, list):
                    return item
                if isinstance(item, dict):
                    return [item]

    # 혹시 body 바로 아래에 data가 있는 경우
    body = data.get("body")
    if isinstance(body, dict):
        body_data = body.get("data")
        if isinstance(body_data, list):
            return body_data

        items = body.get("items")
        if isinstance(items, list):
            return items

    # 기타 fallback
    if isinstance(data.get("data"), list):
        return data["data"]

    if isinstance(data.get("items"), list):
        return data["items"]

    return []


def _parse_cctv_item(item):
    """
    ITS CCTV 한 건을 프론트 타입에 맞는 구조로 변환한다.

    프론트 Cctv 타입은 대략:
    {
      id,
      name,
      roadName,
      region,
      streamUrl,
      isRunning,
      location: { address, lat, lng }
    }
    형태로 사용된다.
    """

    name = (
        item.get("cctvname")
        or item.get("cctvName")
        or item.get("name")
        or "ITS CCTV"
    )

    road = (
        item.get("roadsectionid")
        or item.get("roadName")
        or item.get("roadname")
        or item.get("routeName")
        or "-"
    )

    stream_url = (
        item.get("cctvurl")
        or item.get("cctvUrl")
        or item.get("streamUrl")
        or item.get("url")
    )

    coordx = (
        item.get("coordx")
        or item.get("coordX")
        or item.get("lng")
        or item.get("longitude")
    )

    coordy = (
        item.get("coordy")
        or item.get("coordY")
        or item.get("lat")
        or item.get("latitude")
    )

    address_text = f"{name} / {road or '-'}"

    return {
        "name": str(name),
        "roadName": str(road or "-"),
        "address": address_text,
        "lat": _to_float(coordy),
        "lng": _to_float(coordx),
        "streamUrl": stream_url,
        "region": "기타",
    }


def _is_seoul(name, address_text):
    text = f"{name} {address_text}"
    return "서울" in text or "강남" in text or "서초" in text or "송파" in text


def _is_gyeonggi(name, address_text):
    text = f"{name} {address_text}"
    return (
        "경기" in text
        or "수원" in text
        or "성남" in text
        or "용인" in text
        or "고양" in text
        or "안양" in text
    )


def _to_float(value):
    try:
        return float(value)
    except Exception:
        return None