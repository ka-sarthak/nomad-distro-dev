import json

from nomad_ml_workflows.actions.entries.models import (
    ExportEntriesUserInput,
    SearchSettings,
)

if __name__ == "__main__":
    # For testing purposes
    example_input = ExportEntriesUserInput(
        upload_id="upload_12345",
        user_id="user_67890",
        search_settings=SearchSettings(
            owner="visible",
            query='{"entry_type": "ELNSample"}',
            # required=Required(
            #     include=['results*', 'data.results*'],
            #     exclude=['results.method.method_name'],
            # ),
        ),
        output_file_type="parquet",
    )
    with open("example_input.json", "w") as f:
        json.dump(example_input.search_settings.model_json_schema(), f, indent=4)
