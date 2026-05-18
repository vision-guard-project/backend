import traceback

from flask import Blueprint, request
from app.common.response import success, fail
from app.services import its_cctv_service

cctv_bp = Blueprint("cctv", __name__)


@cctv_bp.get("")
def get_cctvs():
    try:
        return success(its_cctv_service.get_cctvs(), "CCTV 목록 조회 성공")
    except Exception as e:
        print("[CCTV ERROR] get_cctvs 실패")
        traceback.print_exc()
        return fail(str(e), 500)


@cctv_bp.post("/sync")
def sync_cctvs():
    try:
        return success(its_cctv_service.sync_its_cctvs(), "ITS CCTV 동기화 성공")
    except Exception as e:
        print("[CCTV ERROR] sync_cctvs 실패")
        traceback.print_exc()
        return fail(str(e), 500)


@cctv_bp.post("/<cctv_id>/start")
def start_cctv(cctv_id):
    try:
        return success(its_cctv_service.start_cctv(cctv_id), "CCTV 시작 성공")
    except Exception as e:
        print("[CCTV ERROR] start_cctv 실패")
        traceback.print_exc()
        return fail(str(e), 400)


@cctv_bp.post("/<cctv_id>/stop")
def stop_cctv(cctv_id):
    try:
        return success(its_cctv_service.stop_cctv(cctv_id), "CCTV 종료 성공")
    except Exception as e:
        print("[CCTV ERROR] stop_cctv 실패")
        traceback.print_exc()
        return fail(str(e), 400)


@cctv_bp.get("/<cctv_id>/snapshot")
def get_snapshot(cctv_id):
    seconds_ago = int(request.args.get("secondsAgo", 30))

    try:
        return success(
            its_cctv_service.get_snapshot(cctv_id, seconds_ago),
            "스냅샷 조회 성공",
        )
    except Exception as e:
        print("[CCTV ERROR] get_snapshot 실패")
        traceback.print_exc()
        return fail(str(e), 400)