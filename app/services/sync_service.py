# app/services/sync_service.py
from datetime import datetime
import pandas as pd
from app.models import db, Item, SyncLog


class SyncService:
    def __init__(self, spreadsheet_path):
        self.spreadsheet_path = spreadsheet_path

    def sync_spreadsheet(self):
        try:
            # Read spreadsheet
            df = pd.read_csv(self.spreadsheet_path)

            # Track changes
            changes = {
                'created': 0,
                'updated': 0,
                'errors': []
            }

            for _, row in df.iterrows():
                try:
                    self._sync_item(row, changes)
                except Exception as e:
                    changes['errors'].append(f"Error with {row['Serial Number']}: {str(e)}")

            # Log sync
            self._log_sync(changes)

            return changes

        except Exception as e:
            raise SyncError(f"Sync failed: {str(e)}")

    def _sync_item(self, row, changes):
        item = Item.query.filter_by(serial_number=row['Serial Number']).first()

        if item:
            if self._has_changes(item, row):
                self._update_item(item, row)
                changes['updated'] += 1
        else:
            self._create_item(row)
            changes['created'] += 1