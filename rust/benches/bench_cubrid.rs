use criterion::{black_box, criterion_group, criterion_main, Criterion};

use cubrid_benchmark_rust::{
    connect, delete_sequential, drop_table, insert_rows, recreate_table, select_by_pk,
    select_full_scan, table_name, update_indexed,
};

const INSERT_COUNT: i32 = 10_000;
const UPDATE_DELETE_COUNT: i32 = 1_000;

fn bench_insert_10k_sequential(c: &mut Criterion) {
    let table = table_name("insert_10k_cubrid");
    let mut client = connect().expect("connect insert benchmark");
    recreate_table(&mut client, &table).expect("create insert benchmark table");

    c.bench_function("bench_insert_10k_sequential", |b| {
        b.iter(|| {
            insert_rows(&mut client, &table, "insert", INSERT_COUNT).expect("insert rows");
        })
    });

    drop_table(&mut client, &table).expect("drop insert benchmark table");
    client.close().expect("close insert benchmark connection");
}

fn bench_select_10k_by_pk(c: &mut Criterion) {
    let table = table_name("select_by_pk_cubrid");
    let mut client = connect().expect("connect select by pk benchmark");
    recreate_table(&mut client, &table).expect("create select by pk table");

    c.bench_function("bench_select_10k_by_pk", |b| {
        b.iter(|| {
            insert_rows(&mut client, &table, "select", INSERT_COUNT).expect("seed select rows");
            black_box(select_by_pk(&mut client, &table, INSERT_COUNT).expect("select by pk"));
        })
    });

    drop_table(&mut client, &table).expect("drop select by pk table");
    client.close().expect("close select by pk connection");
}

fn bench_select_full_scan(c: &mut Criterion) {
    let table = table_name("select_full_scan_cubrid");
    let mut client = connect().expect("connect full scan benchmark");
    recreate_table(&mut client, &table).expect("create full scan table");

    c.bench_function("bench_select_full_scan", |b| {
        b.iter(|| {
            insert_rows(&mut client, &table, "scan", INSERT_COUNT).expect("seed scan rows");
            black_box(select_full_scan(&mut client, &table).expect("full scan"));
        })
    });

    drop_table(&mut client, &table).expect("drop full scan table");
    client.close().expect("close full scan connection");
}

fn bench_update_1k_where_indexed(c: &mut Criterion) {
    let table = table_name("update_1k_cubrid");
    let mut client = connect().expect("connect update benchmark");
    recreate_table(&mut client, &table).expect("create update table");

    c.bench_function("bench_update_1k_where_indexed", |b| {
        b.iter(|| {
            insert_rows(&mut client, &table, "update", INSERT_COUNT).expect("seed update rows");
            black_box(
                update_indexed(&mut client, &table, UPDATE_DELETE_COUNT).expect("update indexed"),
            );
        })
    });

    drop_table(&mut client, &table).expect("drop update table");
    client.close().expect("close update connection");
}

fn bench_delete_1k_sequential(c: &mut Criterion) {
    let table = table_name("delete_1k_cubrid");
    let mut client = connect().expect("connect delete benchmark");
    recreate_table(&mut client, &table).expect("create delete table");

    c.bench_function("bench_delete_1k_sequential", |b| {
        b.iter(|| {
            insert_rows(&mut client, &table, "delete", INSERT_COUNT).expect("seed delete rows");
            black_box(
                delete_sequential(&mut client, &table, UPDATE_DELETE_COUNT)
                    .expect("delete sequential"),
            );
        })
    });

    drop_table(&mut client, &table).expect("drop delete table");
    client.close().expect("close delete connection");
}

criterion_group!(
    cubrid_benches,
    bench_insert_10k_sequential,
    bench_select_10k_by_pk,
    bench_select_full_scan,
    bench_update_1k_where_indexed,
    bench_delete_1k_sequential,
);
criterion_main!(cubrid_benches);
