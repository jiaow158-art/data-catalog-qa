import pytest
from uuid import uuid4

from app.schemas.database import DatabaseCreate, DatabaseUpdate
from app.schemas.table import TableCreate, TableUpdate
from app.schemas.column import ColumnCreate, ColumnUpdate
from app.schemas.schedule import ScheduleCreate
from app.schemas.report import ReportCreate
from app.services import metadata_service as svc


class TestDatabaseCRUD:
    def test_create(self, db):
        data = DatabaseCreate(name="test_db", display_name="测试库", db_type="hive")
        obj = svc.create_database(db, data)
        assert obj.id is not None
        assert obj.name == "test_db"
        assert obj.display_name == "测试库"

    def test_get(self, db):
        data = DatabaseCreate(name="test_db2", display_name="测试库2")
        obj = svc.create_database(db, data)
        fetched = svc.get_database(db, obj.id)
        assert fetched is not None
        assert fetched.name == "test_db2"

    def test_list(self, db):
        svc.create_database(db, DatabaseCreate(name="list_test_1"))
        svc.create_database(db, DatabaseCreate(name="list_test_2"))
        items, total = svc.list_databases(db, page=1, size=10)
        assert total >= 2

    def test_update(self, db):
        obj = svc.create_database(db, DatabaseCreate(name="update_test"))
        updated = svc.update_database(db, obj.id, DatabaseUpdate(display_name="更新后"))
        assert updated.display_name == "更新后"

    def test_delete(self, db):
        obj = svc.create_database(db, DatabaseCreate(name="delete_test"))
        ok = svc.delete_database(db, obj.id)
        assert ok is True
        assert svc.get_database(db, obj.id) is None

    def test_not_found(self, db):
        assert svc.get_database(db, uuid4()) is None
        assert svc.update_database(db, uuid4(), DatabaseUpdate(display_name="x")) is None
        assert svc.delete_database(db, uuid4()) is False


class TestTableCRUD:
    def test_create_and_detail(self, db):
        db_obj = svc.create_database(db, DatabaseCreate(name="table_test_db"))
        t = svc.create_table(
            db,
            TableCreate(
                database_id=db_obj.id,
                table_name="dw.dwd_order_info",
                display_name="订单明细宽表",
                table_type="dwd",
                primary_keys='["order_id"]',
                owner="张三",
                description="订单明细数据",
            ),
        )
        detail = svc.get_table_detail(db, t.id)
        assert detail is not None
        assert detail.table_name == "dw.dwd_order_info"
        assert detail.columns == []

    def test_list_with_filter(self, db):
        db_obj = svc.create_database(db, DatabaseCreate(name="table_filter_db"))
        svc.create_table(
            db, TableCreate(database_id=db_obj.id, table_name="dwd.a", table_type="dwd")
        )
        svc.create_table(
            db, TableCreate(database_id=db_obj.id, table_name="dws.b", table_type="dws")
        )
        items, total = svc.list_tables(db, table_type="dwd")
        assert total >= 1

    def test_update(self, db):
        db_obj = svc.create_database(db, DatabaseCreate(name="table_update_db"))
        t = svc.create_table(
            db, TableCreate(database_id=db_obj.id, table_name="update_me")
        )
        updated = svc.update_table(
            db, t.id, TableUpdate(display_name="新名字", owner="李四")
        )
        assert updated.display_name == "新名字"
        assert updated.owner == "李四"

    def test_search(self, db):
        db_obj = svc.create_database(db, DatabaseCreate(name="search_db"))
        svc.create_table(
            db,
            TableCreate(
                database_id=db_obj.id,
                table_name="dw.user_info",
                display_name="用户信息表",
                description="存储用户基础信息",
            ),
        )
        items, total = svc.list_tables(db, search="用户")
        assert total >= 1

    def test_delete_cascades(self, db):
        """Deleting a database should cascade-delete its tables."""
        db_obj = svc.create_database(db, DatabaseCreate(name="cascade_db"))
        t = svc.create_table(
            db, TableCreate(database_id=db_obj.id, table_name="cascade_table")
        )
        svc.create_column(
            db, ColumnCreate(table_id=t.id, column_name="col1")
        )
        svc.delete_database(db, db_obj.id)
        assert svc.get_table(db, t.id) is None


class TestColumnCRUD:
    def test_create(self, db):
        db_obj = svc.create_database(db, DatabaseCreate(name="col_test_db"))
        t = svc.create_table(
            db, TableCreate(database_id=db_obj.id, table_name="col_table")
        )
        c = svc.create_column(
            db,
            ColumnCreate(
                table_id=t.id,
                column_name="pay_amount",
                display_name="支付金额",
                data_type="decimal(20,2)",
                description="用户实际支付金额",
                is_primary_key=False,
                calculation_rule="sum(order_pay_amount)",
                enum_values='["微信","支付宝"]',
                sort_order=1,
            ),
        )
        assert c.id is not None
        assert c.column_name == "pay_amount"
        assert c.calculation_rule == "sum(order_pay_amount)"

    def test_list_by_table(self, db):
        db_obj = svc.create_database(db, DatabaseCreate(name="col_list_db"))
        t = svc.create_table(
            db, TableCreate(database_id=db_obj.id, table_name="col_list_table")
        )
        svc.create_column(db, ColumnCreate(table_id=t.id, column_name="a", sort_order=1))
        svc.create_column(db, ColumnCreate(table_id=t.id, column_name="b", sort_order=2))
        items, total = svc.list_columns(db, table_id=t.id)
        assert total == 2

    def test_update(self, db):
        db_obj = svc.create_database(db, DatabaseCreate(name="col_update_db"))
        t = svc.create_table(
            db, TableCreate(database_id=db_obj.id, table_name="col_update_table")
        )
        c = svc.create_column(
            db, ColumnCreate(table_id=t.id, column_name="old_name")
        )
        updated = svc.update_column(
            db, c.id, ColumnUpdate(display_name="新字段名", null_rate=0.05)
        )
        assert updated.display_name == "新字段名"
        assert updated.null_rate == 0.05


class TestScheduleCRUD:
    def test_create_and_link(self, db):
        db_obj = svc.create_database(db, DatabaseCreate(name="sched_db"))
        t = svc.create_table(
            db, TableCreate(database_id=db_obj.id, table_name="sched_table")
        )
        s = svc.create_schedule(
            db,
            ScheduleCreate(
                task_name="dwd_order_daily",
                task_type="spark",
                schedule_desc="每天凌晨3点",
                status="normal",
            ),
        )
        assert s.id is not None
        link = svc.link_table_schedule(db, t.id, s.id, "produces")
        assert link is not None
        assert link.relation_type == "produces"

        # Verify linkage in table detail
        detail = svc.get_table_detail(db, t.id)
        assert len(detail.schedules) == 1
        assert detail.schedules[0].task_name == "dwd_order_daily"


class TestReportCRUD:
    def test_create(self, db):
        r = svc.create_report(
            db,
            ReportCreate(
                report_name="每日销售看板",
                bi_tool="metabase",
                description="展示每日销售汇总",
                owner="分析师小王",
            ),
        )
        assert r.id is not None
        assert r.report_name == "每日销售看板"


class TestSearch:
    def test_global_search(self, db):
        db_obj = svc.create_database(db, DatabaseCreate(name="search_test_db"))
        svc.create_table(
            db,
            TableCreate(
                database_id=db_obj.id,
                table_name="dw.sales_report",
                display_name="销售报表",
            ),
        )
        result = svc.search(db, q="销售")
        assert len(result["tables"]) == 1
        assert result["tables"][0].table_name == "dw.sales_report"
