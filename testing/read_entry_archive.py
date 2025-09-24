from nomad_auto_xrd.common.utils import read_entry_archive


if __name__ == "__main__":
    # Example usage
    entry_id = "BAPOmd_Va_lwSiyiWirDnWQpc4LL"
    upload_id = "qvie_C-5S-OPoYqd3tCAWg"
    user_id = "be691000-501a-462a-99b2-873aa11fbe1e"
    archive = read_entry_archive(entry_id, upload_id, user_id)
    print(archive)
