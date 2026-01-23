from nomad_ml_workflows.actions.entries.utils import merge_files


def test_consolidate_parquet_files():
    file1 = "1.parquet"
    file2 = "2.parquet"
    output_file = "consolidated.parquet"

    merge_files(
        input_file_paths=[file1, file2],
        output_file_path=output_file,
    )


if __name__ == "__main__":
    test_consolidate_parquet_files()
