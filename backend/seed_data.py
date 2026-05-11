"""Seed sample data: simulates a typical data warehouse with ods/dwd/dim/ads layers."""
import uuid
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, engine, Base
from app.models import (
    DatabaseModel,
    Table,
    Column,
    Schedule,
    TableSchedule,
    TableLineage,
)


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Clean existing
    db.query(TableLineage).delete()
    db.query(TableSchedule).delete()
    db.query(Column).delete()
    db.query(Schedule).delete()
    db.query(Table).delete()
    db.query(DatabaseModel).delete()
    db.commit()

    now = datetime.utcnow()

    # ── Databases ──────────────────────────────────────────────
    dbs = {
        "ods": DatabaseModel(
            id=uuid.uuid4(), name="ods", display_name="原始数据层",
            description="操作数据存储层，从业务系统接入的原始数据，保持源系统数据结构",
            db_type="hive", host="hive-prod-01:10000",
            created_at=now - timedelta(days=90),
        ),
        "dwd": DatabaseModel(
            id=uuid.uuid4(), name="dwd", display_name="明细数据层",
            description="数据仓库明细层，对 ODS 数据进行清洗、标准化和轻度汇总",
            db_type="hive", host="hive-prod-01:10000",
            created_at=now - timedelta(days=90),
        ),
        "dim": DatabaseModel(
            id=uuid.uuid4(), name="dim", display_name="维度层",
            description="维度数据层，存储业务维度表和字典表",
            db_type="mysql", host="mysql-dim-01:3306",
            created_at=now - timedelta(days=90),
        ),
        "ads": DatabaseModel(
            id=uuid.uuid4(), name="ads", display_name="应用数据层",
            description="应用数据服务层，面向业务场景的汇总宽表",
            db_type="clickhouse", host="ch-ads-01:8123",
            created_at=now - timedelta(days=60),
        ),
    }
    for d in dbs.values():
        db.add(d)
    db.commit()

    # ── Tables ─────────────────────────────────────────────────
    tables_data = {
        # ODS
        "ods_order_info": {
            "db": "ods", "display_name": "订单原始表", "table_type": "fact",
            "description": "从电商业务库同步的订单主表，每天凌晨2点全量同步",
            "partition_key": "dt", "partition_freq": "daily",
            "owner": "张三", "tags": json.dumps(["ODS", "交易", "核心"]),
            "business_scenarios": "电商交易",
            "usage_notes": "数据量大，查询时务必加 dt 分区过滤",
            "row_count_estimate": 500_000_000,
            "primary_keys": json.dumps(["order_id"]),
        },
        "ods_user_info": {
            "db": "ods", "display_name": "用户原始表", "table_type": "dim",
            "description": "从用户中心同步的用户注册信息表",
            "partition_key": "dt", "partition_freq": "daily",
            "owner": "李四", "tags": json.dumps(["ODS", "用户"]),
            "business_scenarios": "用户画像",
            "usage_notes": "用户敏感信息，查询需审批",
            "row_count_estimate": 20_000_000,
            "primary_keys": json.dumps(["user_id"]),
        },
        "ods_product_info": {
            "db": "ods", "display_name": "商品原始表", "table_type": "dim",
            "description": "从商品管理系统同步的商品基础信息",
            "partition_key": "dt", "partition_freq": "daily",
            "owner": "王五", "tags": json.dumps(["ODS", "商品"]),
            "business_scenarios": "商品管理",
            "usage_notes": "",
            "row_count_estimate": 2_000_000,
            "primary_keys": json.dumps(["product_id"]),
        },
        "ods_payment_log": {
            "db": "ods", "display_name": "支付日志表", "table_type": "fact",
            "description": "从支付网关同步的支付流水日志，增量同步",
            "partition_key": "dt", "partition_freq": "hourly",
            "owner": "张三", "tags": json.dumps(["ODS", "支付", "核心"]),
            "business_scenarios": "支付监控",
            "usage_notes": "增量表，注意去重",
            "row_count_estimate": 800_000_000,
            "primary_keys": json.dumps(["payment_id"]),
        },
        # DWD
        "dwd_order_detail": {
            "db": "dwd", "display_name": "订单明细表", "table_type": "dwd",
            "description": "清洗后的订单明细数据，拆解了商品明细、优惠分摊等",
            "partition_key": "dt", "partition_freq": "daily",
            "owner": "张三", "tags": json.dumps(["DWD", "交易", "核心"]),
            "business_scenarios": "电商交易",
            "usage_notes": "下游 ADS 报表核心依赖表",
            "row_count_estimate": 1_200_000_000,
            "primary_keys": json.dumps(["order_id", "product_id"]),
        },
        "dwd_user_behavior": {
            "db": "dwd", "display_name": "用户行为明细表", "table_type": "dwd",
            "description": "用户浏览、点击、加购、收藏等行为埋点明细",
            "partition_key": "dt", "partition_freq": "daily",
            "owner": "李四", "tags": json.dumps(["DWD", "用户", "埋点"]),
            "business_scenarios": "用户画像, 推荐算法",
            "usage_notes": "埋点量大，建议按 event_type 过滤",
            "row_count_estimate": 5_000_000_000,
            "primary_keys": json.dumps(["event_id"]),
        },
        "dwd_payment_detail": {
            "db": "dwd", "display_name": "支付明细表", "table_type": "dwd",
            "description": "清洗后的支付流水明细，关联订单和用户信息",
            "partition_key": "dt", "partition_freq": "daily",
            "owner": "张三", "tags": json.dumps(["DWD", "支付", "核心"]),
            "business_scenarios": "支付监控, 财务对账",
            "usage_notes": "",
            "row_count_estimate": 800_000_000,
            "primary_keys": json.dumps(["payment_id"]),
        },
        # DIM
        "dim_user": {
            "db": "dim", "display_name": "用户维度表", "table_type": "dim",
            "description": "用户维度宽表，包含用户基本信息、等级、标签",
            "partition_key": "", "partition_freq": "daily",
            "owner": "李四", "tags": json.dumps(["DIM", "用户", "维度"]),
            "business_scenarios": "用户画像, 精准营销",
            "usage_notes": "缓慢变化维，每日全量覆盖",
            "row_count_estimate": 15_000_000,
            "primary_keys": json.dumps(["user_id"]),
        },
        "dim_product": {
            "db": "dim", "display_name": "商品维度表", "table_type": "dim",
            "description": "商品维度宽表，包含商品信息、品类、品牌",
            "partition_key": "", "partition_freq": "daily",
            "owner": "王五", "tags": json.dumps(["DIM", "商品", "维度"]),
            "business_scenarios": "商品分析, 品类运营",
            "usage_notes": "包含一二三级品类层级",
            "row_count_estimate": 2_000_000,
            "primary_keys": json.dumps(["product_id"]),
        },
        "dim_date": {
            "db": "dim", "display_name": "日期维度表", "table_type": "dim",
            "description": "日期维度表，包含年/季/月/周/日及节假日标识",
            "partition_key": "", "partition_freq": "yearly",
            "owner": "管理员", "tags": json.dumps(["DIM", "日期", "维度"]),
            "business_scenarios": "全业务场景",
            "usage_notes": "静态表，每年初更新一次",
            "row_count_estimate": 3650,
            "primary_keys": json.dumps(["date_id"]),
        },
        "dim_region": {
            "db": "dim", "display_name": "地区维度表", "table_type": "dim",
            "description": "全国省市县地区维度，包含区域划分和城市等级",
            "partition_key": "", "partition_freq": "monthly",
            "owner": "管理员", "tags": json.dumps(["DIM", "地区", "维度"]),
            "business_scenarios": "区域分析, 物流调度",
            "usage_notes": "",
            "row_count_estimate": 3300,
            "primary_keys": json.dumps(["region_id"]),
        },
        # ADS
        "ads_user_order_summary": {
            "db": "ads", "display_name": "用户订单汇总表", "table_type": "ads",
            "description": "按用户+日期汇总的订单指标：下单数、金额、优惠金额",
            "partition_key": "dt", "partition_freq": "daily",
            "owner": "张三", "tags": json.dumps(["ADS", "报表", "核心"]),
            "business_scenarios": "运营日报, 用户分析",
            "usage_notes": "BI 日报直接查询此表",
            "row_count_estimate": 300_000_000,
            "primary_keys": json.dumps(["user_id", "dt"]),
        },
        "ads_daily_revenue": {
            "db": "ads", "display_name": "每日营收汇总表", "table_type": "ads",
            "description": "按日汇总全平台营收核心指标：GMV、实收、退款、毛利",
            "partition_key": "dt", "partition_freq": "daily",
            "owner": "张三", "tags": json.dumps(["ADS", "报表", "核心", "财务"]),
            "business_scenarios": "财务日报, 管理层看板",
            "usage_notes": "每天早上 8 点前必须产出",
            "row_count_estimate": 365,
            "primary_keys": json.dumps(["dt"]),
        },
        "ads_product_sales_rank": {
            "db": "ads", "display_name": "商品销量排行表", "table_type": "ads",
            "description": "按商品+日期汇总销量和销售额排名",
            "partition_key": "dt", "partition_freq": "daily",
            "owner": "王五", "tags": json.dumps(["ADS", "报表", "商品"]),
            "business_scenarios": "品类运营, 爆品分析",
            "usage_notes": "",
            "row_count_estimate": 20_000_000,
            "primary_keys": json.dumps(["product_id", "dt"]),
        },
    }

    tables = {}
    for tname, tdata in tables_data.items():
        pk = tdata.pop("primary_keys", None)
        # Convert empty string partition_key to None
        if tdata.get("partition_key") == "":
            tdata["partition_key"] = None
        obj = Table(
            id=uuid.uuid4(),
            table_name=tname,
            database_id=dbs[tdata["db"]].id,
            display_name=tdata["display_name"],
            description=tdata["description"],
            table_type=tdata["table_type"],
            partition_key=tdata.get("partition_key"),
            partition_freq=tdata.get("partition_freq"),
            owner=tdata["owner"],
            tags=tdata.get("tags"),
            business_scenarios=tdata["business_scenarios"],
            usage_notes=tdata["usage_notes"],
            row_count_estimate=tdata["row_count_estimate"],
            primary_keys=pk,
            created_at=now - timedelta(days=30),
        )
        tables[tname] = obj
        db.add(obj)
    db.commit()

    # ── Columns ────────────────────────────────────────────────
    columns_spec = [
        # ods_order_info
        ("ods_order_info", "order_id", "订单ID", "bigint", True, "主键，业务系统自增"),
        ("ods_order_info", "user_id", "用户ID", "bigint", False, "关联用户表"),
        ("ods_order_info", "order_status", "订单状态", "string", False, "待支付/已支付/已发货/已完成/已取消", None, "待支付/已支付/已发货/已完成/已取消"),
        ("ods_order_info", "order_amount", "订单金额(分)", "bigint", False, "原始金额，单位分"),
        ("ods_order_info", "pay_amount", "实付金额(分)", "bigint", False, "优惠后实际支付金额"),
        ("ods_order_info", "create_time", "下单时间", "timestamp", False, ""),
        ("ods_order_info", "dt", "数据日期分区", "string", False, "分区键，格式 YYYY-MM-DD"),
        # ods_user_info
        ("ods_user_info", "user_id", "用户ID", "bigint", True, ""),
        ("ods_user_info", "user_name", "用户名", "string", False, ""),
        ("ods_user_info", "mobile", "手机号", "string", False, "脱敏存储"),
        ("ods_user_info", "register_time", "注册时间", "timestamp", False, ""),
        ("ods_user_info", "user_level", "用户等级", "string", False, "普通/白银/黄金/钻石"),
        ("ods_user_info", "dt", "数据日期分区", "string", False, ""),
        # ods_product_info
        ("ods_product_info", "product_id", "商品ID", "bigint", True, ""),
        ("ods_product_info", "product_name", "商品名称", "string", False, ""),
        ("ods_product_info", "category_id", "一级品类ID", "bigint", False, ""),
        ("ods_product_info", "price", "单价(分)", "bigint", False, ""),
        ("ods_product_info", "dt", "数据日期分区", "string", False, ""),
        # ods_payment_log
        ("ods_payment_log", "payment_id", "支付流水ID", "string", True, ""),
        ("ods_payment_log", "order_id", "关联订单ID", "bigint", False, ""),
        ("ods_payment_log", "pay_channel", "支付渠道", "string", False, "支付宝/微信/银行卡"),
        ("ods_payment_log", "pay_amount", "支付金额(分)", "bigint", False, ""),
        ("ods_payment_log", "pay_time", "支付时间", "timestamp", False, ""),
        ("ods_payment_log", "dt", "数据日期分区", "string", False, ""),
        # dwd_order_detail
        ("dwd_order_detail", "order_id", "订单ID", "bigint", True, ""),
        ("dwd_order_detail", "product_id", "商品ID", "bigint", True, ""),
        ("dwd_order_detail", "user_id", "用户ID", "bigint", False, ""),
        ("dwd_order_detail", "product_quantity", "商品数量", "int", False, ""),
        ("dwd_order_detail", "original_price", "商品原价(分)", "bigint", False, ""),
        ("dwd_order_detail", "discount_amount", "优惠分摊(分)", "bigint", False, "优惠按金额比例分摊到商品"),
        ("dwd_order_detail", "actual_price", "实际成交价(分)", "bigint", False, "original_price - discount_amount"),
        ("dwd_order_detail", "order_status", "订单状态", "string", False, ""),
        ("dwd_order_detail", "dt", "数据日期分区", "string", False, ""),
        # dwd_user_behavior
        ("dwd_user_behavior", "event_id", "事件ID", "string", True, "埋点唯一标识"),
        ("dwd_user_behavior", "user_id", "用户ID", "bigint", False, ""),
        ("dwd_user_behavior", "event_type", "事件类型", "string", False, "page_view/product_click/add_cart/favorite"),
        ("dwd_user_behavior", "product_id", "商品ID", "bigint", False, "若事件涉及商品"),
        ("dwd_user_behavior", "page_url", "页面URL", "string", False, ""),
        ("dwd_user_behavior", "duration_ms", "停留时长(毫秒)", "bigint", False, ""),
        ("dwd_user_behavior", "event_time", "事件时间", "timestamp", False, ""),
        ("dwd_user_behavior", "dt", "数据日期分区", "string", False, ""),
        # dwd_payment_detail
        ("dwd_payment_detail", "payment_id", "支付流水ID", "string", True, ""),
        ("dwd_payment_detail", "order_id", "订单ID", "bigint", False, ""),
        ("dwd_payment_detail", "user_id", "用户ID", "bigint", False, ""),
        ("dwd_payment_detail", "pay_channel", "支付渠道", "string", False, ""),
        ("dwd_payment_detail", "pay_amount", "支付金额(分)", "bigint", False, ""),
        ("dwd_payment_detail", "pay_status", "支付状态", "string", False, "成功/失败/处理中"),
        ("dwd_payment_detail", "pay_time", "支付时间", "timestamp", False, ""),
        ("dwd_payment_detail", "dt", "数据日期分区", "string", False, ""),
        # dim_user
        ("dim_user", "user_id", "用户ID", "bigint", True, ""),
        ("dim_user", "user_name", "用户名", "string", False, ""),
        ("dim_user", "mobile", "手机号", "string", False, "脱敏"),
        ("dim_user", "user_level", "用户等级", "string", False, "普通/白银/黄金/钻石"),
        ("dim_user", "city", "所在城市", "string", False, ""),
        ("dim_user", "register_date", "注册日期", "date", False, ""),
        ("dim_user", "first_order_date", "首单日期", "date", False, "用户首次下单日期"),
        ("dim_user", "total_order_count", "累计订单数", "bigint", False, "截至昨天的累计"),
        ("dim_user", "total_order_amount", "累计消费金额(分)", "bigint", False, "截至昨天的累计"),
        # dim_product
        ("dim_product", "product_id", "商品ID", "bigint", True, ""),
        ("dim_product", "product_name", "商品名称", "string", False, ""),
        ("dim_product", "cat1_name", "一级品类", "string", False, "服饰/数码/食品/美妆"),
        ("dim_product", "cat2_name", "二级品类", "string", False, ""),
        ("dim_product", "cat3_name", "三级品类", "string", False, ""),
        ("dim_product", "brand_name", "品牌", "string", False, ""),
        ("dim_product", "price", "标准售价(分)", "bigint", False, ""),
        ("dim_product", "status", "商品状态", "string", False, "在售/下架/缺货"),
        # dim_date
        ("dim_date", "date_id", "日期ID", "int", True, "格式 YYYYMMDD"),
        ("dim_date", "date_str", "日期", "date", False, ""),
        ("dim_date", "year", "年", "int", False, ""),
        ("dim_date", "quarter", "季度", "int", False, "1-4"),
        ("dim_date", "month", "月", "int", False, "1-12"),
        ("dim_date", "day", "日", "int", False, "1-31"),
        ("dim_date", "weekday", "星期", "int", False, "1=周一"),
        ("dim_date", "is_holiday", "是否节假日", "boolean", False, ""),
        ("dim_date", "holiday_name", "节日名称", "string", False, ""),
        # dim_region
        ("dim_region", "region_id", "地区ID", "int", True, ""),
        ("dim_region", "province", "省", "string", False, ""),
        ("dim_region", "city", "市", "string", False, ""),
        ("dim_region", "district", "区/县", "string", False, ""),
        ("dim_region", "region_level", "城市等级", "string", False, "一线/新一线/二线/三线/四线"),
        # ads_user_order_summary
        ("ads_user_order_summary", "user_id", "用户ID", "bigint", True, ""),
        ("ads_user_order_summary", "dt", "统计日期", "string", True, "分区键"),
        ("ads_user_order_summary", "order_count", "下单数", "bigint", False, ""),
        ("ads_user_order_summary", "order_amount", "下单金额(分)", "bigint", False, ""),
        ("ads_user_order_summary", "pay_amount", "实付金额(分)", "bigint", False, ""),
        ("ads_user_order_summary", "discount_amount", "优惠金额(分)", "bigint", False, ""),
        ("ads_user_order_summary", "avg_order_amount", "客单价(分)", "bigint", False, "pay_amount / order_count"),
        # ads_daily_revenue
        ("ads_daily_revenue", "dt", "统计日期", "string", True, ""),
        ("ads_daily_revenue", "gmv", "GMV(分)", "bigint", False, "下单总金额"),
        ("ads_daily_revenue", "actual_revenue", "实收(分)", "bigint", False, "实际到账金额"),
        ("ads_daily_revenue", "refund_amount", "退款金额(分)", "bigint", False, ""),
        ("ads_daily_revenue", "order_count", "订单数", "bigint", False, ""),
        ("ads_daily_revenue", "pay_user_count", "支付用户数", "bigint", False, ""),
        ("ads_daily_revenue", "new_user_count", "新用户数", "bigint", False, "当日首次下单"),
        # ads_product_sales_rank
        ("ads_product_sales_rank", "product_id", "商品ID", "bigint", True, ""),
        ("ads_product_sales_rank", "dt", "统计日期", "string", True, ""),
        ("ads_product_sales_rank", "sale_count", "销量", "bigint", False, ""),
        ("ads_product_sales_rank", "sale_amount", "销售额(分)", "bigint", False, ""),
        ("ads_product_sales_rank", "sale_rank", "销量排名", "int", False, "当日品类内排名"),
        ("ads_product_sales_rank", "product_name", "商品名称", "string", False, "冗余字段方便查询"),
        ("ads_product_sales_rank", "cat1_name", "一级品类", "string", False, "冗余"),
    ]

    for idx, (tname, col_name, display, dtype, is_pk, desc, *rest) in enumerate(columns_spec):
        enum_vals = rest[0] if rest else None
        calc_rule = None
        # Some columns have calculation rules
        if col_name == "actual_price":
            calc_rule = "original_price - discount_amount"
        elif col_name == "avg_order_amount":
            calc_rule = "pay_amount / order_count"
        elif col_name in ("total_order_count", "total_order_amount"):
            calc_rule = f"SUM({col_name}) FROM dwd_order_detail GROUP BY user_id"

        obj = Column(
            id=uuid.uuid4(),
            table_id=tables[tname].id,
            column_name=col_name,
            display_name=display,
            data_type=dtype,
            description=desc,
            is_primary_key=is_pk,
            is_nullable=not is_pk,
            enum_values=json.dumps(enum_vals.split("/")) if enum_vals else None,
            calculation_rule=calc_rule,
            sort_order=idx,
        )
        db.add(obj)
    db.commit()

    # ── Schedules ──────────────────────────────────────────────
    schedules = [
        ("ods_order_sync", "SQL", "0 2 * * *", "每天凌晨2点全量同步订单数据", "张三", now - timedelta(hours=5), None, 3420, "success"),
        ("ods_user_sync", "Python", "0 3 * * *", "每天凌晨3点同步用户数据", "李四", now - timedelta(hours=4), None, 120, "success"),
        ("ods_product_sync", "Python", "0 3 * * *", "每天凌晨3点同步商品数据", "王五", now - timedelta(hours=4), None, 580, "success"),
        ("ods_payment_sync", "Python", "0 * * * *", "每小时同步支付流水", "张三", now - timedelta(minutes=30), None, 95, "success"),
        ("dwd_order_etl", "Spark", "0 5 * * *", "ODS订单清洗写入DWD明细层", "张三", now - timedelta(hours=2), None, 4800, "success"),
        ("dwd_behavior_etl", "Spark", "0 5 * * *", "埋点数据解析写入DWD行为明细", "李四", None, now - timedelta(hours=2), None, "failed"),
        ("dwd_payment_etl", "Spark", "0 5 * * *", "支付流水清洗写入DWD支付明细", "张三", now - timedelta(hours=2), None, 2100, "success"),
        ("dim_user_refresh", "Spark", "0 7 * * *", "每日全量刷新用户维度表", "李四", now - timedelta(minutes=50), None, 3600, "success"),
        ("dim_product_refresh", "Spark", "0 7 * * *", "每日全量刷新商品维度表", "王五", now - timedelta(minutes=50), None, 2400, "success"),
        ("ads_user_summary", "Spark", "0 8 * * *", "计算用户订单汇总写入ADS", "张三", now - timedelta(minutes=20), None, 1200, "success"),
        ("ads_daily_revenue", "Spark", "0 8 * * *", "计算每日营收指标写入ADS", "张三", now - timedelta(minutes=20), None, 600, "success"),
        ("ads_product_rank", "Spark", "0 8 * * *", "计算商品销量排行写入ADS", "王五", now - timedelta(minutes=20), None, 900, "running"),
    ]

    sch_objs = {}
    for (name, ttype, cron, desc, owner, lst, lft, dur, status) in schedules:
        obj = Schedule(
            id=uuid.uuid4(),
            task_name=name,
            task_type=ttype,
            schedule_cron=cron,
            schedule_desc=desc,
            owner=owner,
            last_success_time=lst,
            last_failure_time=lft,
            last_duration_sec=dur,
            status=status,
            created_at=now - timedelta(days=60),
        )
        sch_objs[name] = obj
        db.add(obj)
    db.commit()

    # ── Table-Schedule links ───────────────────────────────────
    links = [
        ("ods_order_info", "ods_order_sync"),
        ("ods_user_info", "ods_user_sync"),
        ("ods_product_info", "ods_product_sync"),
        ("ods_payment_log", "ods_payment_sync"),
        ("dwd_order_detail", "dwd_order_etl"),
        ("dwd_user_behavior", "dwd_behavior_etl"),
        ("dwd_payment_detail", "dwd_payment_etl"),
        ("dim_user", "dim_user_refresh"),
        ("dim_product", "dim_product_refresh"),
        ("ads_user_order_summary", "ads_user_summary"),
        ("ads_daily_revenue", "ads_daily_revenue"),
        ("ads_product_sales_rank", "ads_product_rank"),
    ]
    for tname, sname in links:
        db.add(TableSchedule(
            id=uuid.uuid4(),
            table_id=tables[tname].id,
            schedule_id=sch_objs[sname].id,
            relation_type="produces",
        ))
    db.commit()

    # ── Table Lineage ──────────────────────────────────────────
    lineage_links = [
        ("ods_order_info", "dwd_order_detail", "清洗+拆解优惠"),
        ("ods_user_info", "dim_user", "全量刷新"),
        ("ods_product_info", "dim_product", "全量刷新"),
        ("ods_payment_log", "dwd_payment_detail", "清洗+关联订单"),
        ("dwd_order_detail", "ads_user_order_summary", "按用户+日期汇总"),
        ("dwd_order_detail", "ads_daily_revenue", "按日期汇总营收"),
        ("dwd_order_detail", "ads_product_sales_rank", "按商品+日期汇总排名"),
        ("dwd_payment_detail", "ads_daily_revenue", "按日期汇总实收"),
        ("dim_user", "ads_user_order_summary", "关联用户属性"),
        ("dim_product", "ads_product_sales_rank", "关联商品品类"),
    ]
    for upstream, downstream, desc in lineage_links:
        db.add(TableLineage(
            id=uuid.uuid4(),
            upstream_table_id=tables[upstream].id,
            downstream_table_id=tables[downstream].id,
            relation_desc=desc,
        ))
    db.commit()

    db.close()
    print("Seed data inserted successfully!")
    print(f"  Databases: {len(dbs)}")
    print(f"  Tables: {len(tables)}")
    print(f"  Columns: {len(columns_spec)}")
    print(f"  Schedules: {len(schedules)}")
    print(f"  Table-Schedule links: {len(links)}")
    print(f"  Lineage links: {len(lineage_links)}")


if __name__ == "__main__":
    seed()
