from app.extensions import db
from app.models.cctv import Cctv


def find_all():
    return Cctv.query.order_by(Cctv.id.asc()).all()


def find_by_id(cctv_id):
    return Cctv.query.get(cctv_id)


def replace_two_cctvs(cctv_items):
    """
    MVP 기준:
    ITS에서 받은 CCTV 중 서울/경기 2대만 DB에 저장.
    기존 데이터는 단순화해서 전체 삭제 후 재저장.
    """
    Cctv.query.delete()

    for item in cctv_items:
        cctv = Cctv(
            name=item["name"],
            road_name=item.get("roadName"),
            address=item.get("address"),
            latitude=item.get("lat"),
            longitude=item.get("lng"),
            stream_url=item.get("streamUrl"),
            region=item.get("region"),
        )
        db.session.add(cctv)

    db.session.commit()
    return find_all()


def save(cctv):
    db.session.add(cctv)
    db.session.commit()
    return cctv