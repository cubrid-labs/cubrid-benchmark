from __future__ import annotations

from collections.abc import Generator
from datetime import datetime, timezone

import pytest
from pytest_benchmark.fixture import BenchmarkFixture
from sqlalchemy import DateTime, Integer, String, create_engine, select, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass


class BenchUser(Base):
    __tablename__ = "bench_users"  # pyright: ignore[reportUnannotatedClassAttribute]

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(200))
    age: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime)


SessionFactory = sessionmaker[Session]


def _build_user(index: int, prefix: str) -> BenchUser:
    return BenchUser(
        name=f"{prefix}_{index:05d}",
        email=f"{prefix}_{index:05d}@example.com",
        age=20 + (index % 50),
        created_at=datetime.now(timezone.utc).replace(tzinfo=None),
    )


def _clear_users(engine: Engine) -> None:
    with engine.begin() as connection:
        _ = connection.execute(text("DELETE FROM bench_users"))


def _seed_users(session_factory: SessionFactory, engine: Engine, count: int, prefix: str) -> None:
    _clear_users(engine)
    with session_factory() as session:
        session.add_all(_build_user(index, prefix) for index in range(1, count + 1))
        session.commit()


@pytest.fixture(scope="module")
def cubrid_engine() -> Generator[Engine, None, None]:
    engine = create_engine("cubrid+pycubrid://dba@localhost:33000/benchdb")
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture(scope="module")
def cubrid_session_factory(cubrid_engine: Engine) -> SessionFactory:
    return sessionmaker(bind=cubrid_engine, expire_on_commit=False)


@pytest.fixture(autouse=True)
def cleanup_bench_users(cubrid_engine: Engine) -> Generator[None, None, None]:
    _clear_users(cubrid_engine)
    try:
        yield
    finally:
        _clear_users(cubrid_engine)


def _run_single_row_crud(session_factory: SessionFactory, engine: Engine) -> None:
    _clear_users(engine)
    with session_factory() as session:
        user = _build_user(1, "crud")
        session.add(user)
        session.commit()
        user_id = user.id

    with session_factory() as session:
        selected = session.get(BenchUser, user_id)
        assert selected is not None
        selected.age += 1
        session.commit()

    with session_factory() as session:
        selected = session.get(BenchUser, user_id)
        assert selected is not None
        session.delete(selected)
        session.commit()


def _run_bulk_insert(session_factory: SessionFactory, engine: Engine, count: int) -> None:
    _clear_users(engine)
    with session_factory() as session:
        session.add_all(_build_user(index, f"bulk_{count}") for index in range(1, count + 1))
        session.commit()


def _run_query_builder_select(session_factory: SessionFactory, engine: Engine) -> None:
    _seed_users(session_factory, engine, count=1000, prefix="orm_select")
    with session_factory() as session:
        rows = session.execute(select(BenchUser).order_by(BenchUser.id)).scalars().all()
        assert len(rows) == 1000


def _run_raw_sql_select(session_factory: SessionFactory, engine: Engine) -> None:
    _seed_users(session_factory, engine, count=1000, prefix="raw_select")
    with session_factory() as session:
        rows = session.execute(
            text("SELECT id, name, email, age, created_at FROM bench_users ORDER BY id")
        ).all()
        assert len(rows) == 1000


def test_bench_single_row_crud(
    benchmark: BenchmarkFixture,
    cubrid_session_factory: SessionFactory,
    cubrid_engine: Engine,
) -> None:
    benchmark.pedantic(  # pyright: ignore[reportUnknownMemberType]
        _run_single_row_crud,
        args=(cubrid_session_factory, cubrid_engine),
        rounds=5,
        warmup_rounds=1,
    )


@pytest.mark.parametrize("count", [100, 1000], ids=["100", "1000"])
def test_bench_bulk_insert(
    benchmark: BenchmarkFixture,
    cubrid_session_factory: SessionFactory,
    cubrid_engine: Engine,
    count: int,
) -> None:
    benchmark.pedantic(  # pyright: ignore[reportUnknownMemberType]
        _run_bulk_insert,
        args=(cubrid_session_factory, cubrid_engine, count),
        rounds=5,
        warmup_rounds=1,
    )


def test_bench_query_builder_select_all(
    benchmark: BenchmarkFixture,
    cubrid_session_factory: SessionFactory,
    cubrid_engine: Engine,
) -> None:
    benchmark.pedantic(  # pyright: ignore[reportUnknownMemberType]
        _run_query_builder_select,
        args=(cubrid_session_factory, cubrid_engine),
        rounds=5,
        warmup_rounds=1,
    )


def test_bench_raw_sql_select_all(
    benchmark: BenchmarkFixture,
    cubrid_session_factory: SessionFactory,
    cubrid_engine: Engine,
) -> None:
    benchmark.pedantic(  # pyright: ignore[reportUnknownMemberType]
        _run_raw_sql_select,
        args=(cubrid_session_factory, cubrid_engine),
        rounds=5,
        warmup_rounds=1,
    )


@pytest.mark.skip(reason="TODO: add relationship/join loading benchmarks once schema has foreign keys")
def test_bench_relationship_join_loading() -> None:
    pass
