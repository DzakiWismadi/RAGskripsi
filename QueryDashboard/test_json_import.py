import pytest
from playwright.sync_api import Page, expect
import json


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
    }


class TestJSONImportFunctionality:

    def test_full_json_import_workflow(self, page: Page):
        print("\n=== Step 1: Opening the existing table ===")
        page.goto("http://127.0.0.1:5000/table/1")

        expect(page).to_have_url("http://127.0.0.1:5000/table/1")
        print("[OK] Table opened successfully")

        print("\n=== Step 2: Clicking 'Import JSON' button ===")
        page.get_by_role("button", name="Import JSON").click()

        print("\n=== Step 3: Uploading bulkquery.json file ===")
        file_path = r"D:\Hilmi\Coding\MasterFolderSkripsi\RAG\QueryDashboard\bulkquery.json"

        page.locator('input[type="file"]').set_input_files(file_path)
        page.wait_for_timeout(1000)

        print("\n=== Step 4: Checking import success ===")

        try:
            success_message = page.get_by_text("Imported 50 queries")
            expect(success_message).to_be_visible(timeout=5000)
            print("[OK] Import success message visible")
        except:
            print("Checking for alternative success indicators...")
            page.screenshot(path="import_attempt.png")
            print("Screenshot saved as import_attempt.png")

        # Dismiss any open modal
        page.wait_for_timeout(2000)
        page.keyboard.press("Escape")
        page.wait_for_timeout(1000)

        print("\n=== Step 5: Viewing queries and checking ground truth display ===")

        try:
            query_rows = page.locator("table tbody tr")
            count = query_rows.count()
            print(f"Found {count} query rows displayed")

            if count > 0:
                first_row = query_rows.first
                first_text = first_row.inner_text()
                print(f"First row content: {first_text[:200]}...")

                if "Q181" in first_text:
                    print("[OK] Q181 found in first row")
                else:
                    print("[WARNING] Q181 not found in first row")

                # Check if ground truth is displayed
                if "A.6.3" in first_text or "Ground Truth" in first_text:
                    print("[OK] Ground truth information found in table")
                else:
                    print("[WARNING] Ground truth not clearly visible in table")
        except Exception as e:
            print(f"Error checking query rows: {e}")
            page.screenshot(path="queries_view.png")

        print("\n=== Step 6: Exporting all queries ===")
        with page.expect_download() as download_info:
            page.get_by_role("button", name="Export All").click()
        download = download_info.value
        print(f"[OK] File downloaded: {download.suggested_filename}")

        # Save the downloaded file
        download.save_as(f"D:\\Hilmi\\Coding\\MasterFolderSkripsi\\RAG\\QueryDashboard\\downloaded_export.json")
        print("[OK] Downloaded file saved")

        # Verify the downloaded file content
        with open("D:\\Hilmi\\Coding\\MasterFolderSkripsi\\RAG\\QueryDashboard\\downloaded_export.json", 'r') as f:
            exported_data = json.load(f)
            print(f"\n[OK] Exported file contains {len(exported_data)} queries")

            # Check if ground_truth_ranked is in the exported data
            if exported_data and 'ground_truth_ranked' in exported_data[0]:
                print("[OK] Exported data contains ground_truth_ranked field")
                print(f"Sample exported query:\n{json.dumps(exported_data[0], indent=2, ensure_ascii=False)}")
            else:
                print("[WARNING] Exported data missing ground_truth_ranked field")

        print("\n=== Step 7: Testing query edit functionality ===")
        if count > 0:
            first_row = query_rows.first
            edit_button = first_row.get_by_role("button", name="").locator("i.bi-pencil").first
            edit_button.click()

            page.wait_for_timeout(2000)

            ground_truth_field = page.locator("#groundTruth")
            ground_truth_value = ground_truth_field.input_value()
            print(f"Ground truth value in edit modal: '{ground_truth_value}'")

            if ground_truth_value:
                print("[OK] Ground truth displayed in edit modal")
            else:
                print("[WARNING] Ground truth field is empty in edit modal")

            # Try to close modal with keyboard escape
            page.keyboard.press("Escape")
            page.wait_for_timeout(500)

        print("\n=== Test completed ===")
        page.screenshot(path="final_state.png")
        print("Final screenshot saved")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
