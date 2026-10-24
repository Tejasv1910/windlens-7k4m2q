
import httpx

BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1"

PARAMS = {
    "publishDateTimeFrom": "2026-01-01T00:00:00Z",
    "publishDateTimeTo": "2026-01-02T00:00:00Z",
}

def main():
    url = f"{BASE_URL}/datasets/WINDFOR/stream"

    with httpx.Client(timeout=60.0) as client:
        response = client.get(url, params=PARAMS)

        print("URL:", response.url)
        print("HTTP status:", response.status_code)

        if response.status_code != 200:
            print("Error details:", response.text[:2000])
            response.raise_for_status()

        records = response.json()

        if not isinstance(records, list):
            print("Unexpected response:", str(records)[:2000])
            return

        print("Record count:", len(records))

        if not records:
            print("No forecast records found for this publication window.")
            return

        publication_times = sorted({
            r["publishTime"]
            for r in records
            if r.get("publishTime")
        })

        print("Distinct publication times:", len(publication_times))
        print("First 10 publication times:", publication_times[:10])
        print("Last 10 publication times:", publication_times[-10:])

        delivery_times = [
            r["startTime"] for r in records if r.get("startTime")
        ]

        if delivery_times:
            print("Earliest delivery:", min(delivery_times))
            print("Latest delivery:", max(delivery_times))

        print("\nFirst 5 records:")
        for record in records[:5]:
            print(record)

if __name__ == "__main__":
    main()
