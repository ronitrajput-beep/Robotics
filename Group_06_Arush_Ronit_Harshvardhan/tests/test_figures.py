import sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'analytics'))
from generate_paper_figures import generate_publication_assets


class FigureIntegrityChecks(unittest.TestCase):
    def test_starter_data_rejected_without_mutation(self):
        root = Path(__file__).resolve().parents[1]
        source = root / 'analytics/SIMULATED_solar_cleaning_benchmark.csv'
        before = source.read_bytes()
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'figure.png'
            with self.assertRaises(ValueError):
                generate_publication_assets(source, target)
            self.assertFalse(target.exists())
        self.assertEqual(source.read_bytes(), before)

    def test_existing_figure_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'figure.png'
            target.write_bytes(b'preserve')
            with self.assertRaises(FileExistsError):
                generate_publication_assets('unused.csv', target)
            self.assertEqual(target.read_bytes(), b'preserve')
