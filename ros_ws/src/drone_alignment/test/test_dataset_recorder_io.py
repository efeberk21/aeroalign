"""Check the recorder's real file-writing helper without a ROS installation."""

import ast
import base64
import csv
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


SOURCE = Path(__file__).parents[1] / 'drone_alignment' / 'dataset_recorder.py'
PNG = base64.b64decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8'
    '/x8AAusB9Wl6WQAAAABJRU5ErkJggg=='
)


def load_io_helper():
    """Execute the production helper unchanged, excluding ROS-only imports."""
    if not SOURCE.is_file():
        raise AssertionError('The CSV recorder implementation is missing')
    tree = ast.parse(SOURCE.read_text(encoding='utf-8'))
    selected = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            if any(isinstance(t, ast.Name) and t.id == 'MANIFEST_FIELDS'
                   for t in node.targets):
                selected.append(node)
        elif isinstance(node, ast.FunctionDef) and node.name == 'write_record':
            selected.append(node)
    namespace = {'csv': csv}
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(SOURCE), 'exec'),
         namespace)
    return namespace['MANIFEST_FIELDS'], namespace['write_record']


class RecorderFileTests(unittest.TestCase):
    def setUp(self):
        self.fields, self.write_record = load_io_helper()
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.folder = Path(self.temporary.name)
        self.manifest = self.folder / 'manifest.csv'
        with self.manifest.open('x', newline='', encoding='utf-8') as stream:
            csv.DictWriter(stream, fieldnames=self.fields).writeheader()
        self.row = {
            'image_id': 'scene01_session01_frame000001',
            'scene_id': 'scene01',
            'session_id': 'session01',
            'image_path': 'scene01_session01_frame000001.png',
            'source_stamp_ns': 1234567890123456789,
            'width': 640,
            'height': 480,
            'platform_variant': 'orange_h_v1',
            'ground_variant': 'matte_gray_v1',
            'light_variant': 'sun_default_v1',
            'nominal_height_m': 7.5,
            'notes': 'merkez, "gölge"\nikinci satır',
            'camera_profile': 'iris_wide_640x480_hfov2_zoom1',
        }
        self.image = self.folder / self.row['image_path']

    def test_image_matches_metadata_and_csv_quotes_round_trip(self):
        self.write_record(self.image, self.manifest, PNG, self.row)
        self.assertEqual(self.image.read_bytes(), PNG)
        with self.manifest.open(newline='', encoding='utf-8') as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 1)
        for key, value in self.row.items():
            self.assertEqual(rows[0][key], str(value))

    def test_collision_preserves_existing_image_and_manifest(self):
        self.image.write_bytes(b'previous image must survive')
        before = self.manifest.read_bytes()
        with self.assertRaises(FileExistsError):
            self.write_record(self.image, self.manifest, PNG, self.row)
        self.assertEqual(self.image.read_bytes(), b'previous image must survive')
        self.assertEqual(self.manifest.read_bytes(), before)

    def test_partial_csv_failure_restores_previous_records_and_allows_retry(self):
        self.write_record(self.image, self.manifest, PNG, self.row)
        before = self.manifest.read_bytes()
        second = dict(self.row, image_id='second', image_path='second.png')
        second_image = self.folder / 'second.png'

        class FailingWriter:
            def __init__(self, stream, **kwargs):
                self.stream = stream

            def writerow(self, row):
                self.stream.write('incomplete,row')
                self.stream.flush()
                raise OSError('simulated storage failure')

        with patch.object(csv, 'DictWriter', FailingWriter):
            with self.assertRaises(OSError):
                self.write_record(second_image, self.manifest, PNG, second)
        self.assertEqual(self.manifest.read_bytes(), before)
        self.assertEqual(self.image.read_bytes(), PNG)
        self.assertFalse(second_image.exists())
        self.write_record(second_image, self.manifest, PNG, second)
        with self.manifest.open(newline='', encoding='utf-8') as stream:
            self.assertEqual(len(list(csv.DictReader(stream))), 2)

    def test_missing_manifest_does_not_leave_an_unlisted_image(self):
        self.manifest.unlink()
        with self.assertRaises(FileNotFoundError):
            self.write_record(self.image, self.manifest, PNG, self.row)
        self.assertFalse(self.image.exists())

    def test_unknown_height_remains_blank(self):
        row = dict(self.row, nominal_height_m='')
        self.write_record(self.image, self.manifest, PNG, row)
        with self.manifest.open(newline='', encoding='utf-8') as stream:
            self.assertEqual(next(csv.DictReader(stream))['nominal_height_m'], '')


if __name__ == '__main__':
    unittest.main()
