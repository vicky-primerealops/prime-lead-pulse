# Matrix MLS Data Export Plan (Last 12 Months)

Because Beaches MLS has a hard cap of 5,000 results and their web interface blocks automated bots from finding the buttons reliably, the safest and fastest way to get 100% of your data without missing a single property is this manual filter plan. 

By following this grid, you guarantee **no duplicates** and **no missing records**.

## The 3-Step Search Formula

For every date range in the schedule below, you will run exactly **3 separate searches**. 

### 1. The "Closed" Search
*   **Property Type:** Check ALL boxes (Residential, Commercial, etc.)
*   **Status:** Check **ONLY** `Closed`
*   **Date Box:** Enter the date chunk into the `Closed` date box.
*   *Failsafe:* If this hits 5,000+, split it by Property Type (Run Residential by itself, then run the rest).

### 2. The "Active & Pending" Search
*   **Property Type:** Check ALL boxes 
*   **Status:** Check `Active`, `Pending`, `Coming Soon`, and `Active Under Contract`.
*   **Date Box:** Enter the date chunk into the date boxes for *each* of those statuses.

### 3. The "Off-Market" Search
*   **Property Type:** Check ALL boxes 
*   **Status:** Check `Withdrawn`, `Expired`, `Canceled`, and `Temp Off Market`.
*   **Date Box:** Enter the date chunk into the date boxes for *each* of those statuses.

---

## Your 12-Month Date Schedule
*Copy and paste these exact chunks into the date boxes for the searches above. Work your way down the list.*

| Batch # | Date Range | Notes |
| :--- | :--- | :--- |
| **Batch 1** | `07/25/2025-07/31/2025` | *Start* |
| **Batch 2** | `08/01/2025-08/31/2025` | |
| **Batch 3** | `09/01/2025-09/30/2025` | |
| **Batch 4** | `10/01/2025-10/31/2025` | |
| **Batch 5** | `11/01/2025-11/30/2025` | |
| **Batch 6** | `12/01/2025-12/31/2025` | |
| **Batch 7** | `01/01/2026-01/31/2026` | |
| **Batch 8** | `02/01/2026-02/28/2026` | |
| **Batch 9** | `03/01/2026-03/31/2026` | |
| **Batch 10** | `04/01/2026-04/30/2026` | |
| **Batch 11** | `05/01/2026-05/31/2026` | |
| **Batch 12** | `06/01/2026-06/30/2026` | |
| **Batch 13** | `07/01/2026-07/25/2026` | *End* |

---

## What to do with the files?
As you export these batches using your custom "LA" format, save all the CSVs directly into the `mls_exports` folder on your Desktop. 

Once you are done, run the `python merge_mls_data.py` script we created earlier. It will instantly combine all the files, remove any accidental duplicates using the MLS#, and give you one perfect master spreadsheet.
