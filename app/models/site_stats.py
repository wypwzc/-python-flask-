"""
站点访问统计模型
按天记录 PV/UV/IP 数据
"""
from app import db
from datetime import datetime


class SiteStats(db.Model):
    """站点访问统计表"""
    __tablename__ = 'site_stats'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date, unique=True, nullable=False, comment='统计日期')
    pv = db.Column(db.Integer, default=0, comment='页面浏览量')
    uv = db.Column(db.Integer, default=0, comment='独立访客数')
    ip_count = db.Column(db.Integer, default=0, comment='独立 IP 数')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    @classmethod
    def get_total_stats(cls):
        """获取全站累计统计"""
        from sqlalchemy import func
        total = cls.query.with_entities(
            func.sum(cls.pv).label('total_pv'),
            func.sum(cls.uv).label('total_uv')
        ).first()
        return {
            'total_pv': total.total_pv or 0,
            'total_uv': total.total_uv or 0
        }

    @classmethod
    def get_recent_days(cls, days=7):
        """获取最近 N 天的统计数据"""
        from datetime import datetime, timedelta
        today = datetime.now().date()
        start_date = today - timedelta(days=days - 1)
        records = cls.query.filter(cls.date >= start_date)\
            .order_by(cls.date.asc()).all()

        # 补全没有记录的日期
        result = []
        date_map = {r.date: r for r in records}
        for i in range(days):
            date = start_date + timedelta(days=i)
            if date in date_map:
                result.append(date_map[date])
            else:
                # 创建空的统计对象
                stats = cls(date=date, pv=0, uv=0)
                result.append(stats)
        return result

    def __repr__(self):
        return f'<SiteStats {self.date}>'
