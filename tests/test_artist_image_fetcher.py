import tempfile
import unittest
from pathlib import Path
from unittest import mock

from PIL import Image

from src.clipped.artist_image_fetcher import ArtistImageFetcher


class ArtistImageFetcherLogoCleanupTests(unittest.TestCase):
    def test_skips_existing_transparent_logo(self):
        fetcher = ArtistImageFetcher()

        with tempfile.TemporaryDirectory() as tmpdir:
            logo_path = Path(tmpdir) / "logo.png"
            img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
            img.save(logo_path)

            self.assertFalse(fetcher.should_clean_logo(logo_path))

    def test_runs_rmbg_in_logo_mode_for_black_background_logo(self):
        fetcher = ArtistImageFetcher()

        with tempfile.TemporaryDirectory() as tmpdir:
            logo_path = Path(tmpdir) / "logo.png"
            Image.new("RGB", (64, 64), (0, 0, 0)).save(logo_path)

            rmbg_path = Path(tmpdir) / "rmbg"
            rmbg_path.write_text("#!/bin/bash\nexit 0\n", encoding="utf-8")
            rmbg_path.chmod(0o755)

            with mock.patch("subprocess.run") as run_mock, mock.patch.object(fetcher, "log"):
                run_mock.return_value.returncode = 0
                run_mock.return_value.stdout = ""
                run_mock.return_value.stderr = ""

                fetcher.clean_logo_background(logo_path, rmbg_path=rmbg_path)

                args = run_mock.call_args[0][0]
                self.assertIn(str(rmbg_path), args)
                self.assertIn("--background", args)
                self.assertIn("black", args)
                self.assertIn("--logo", args)


if __name__ == "__main__":
    unittest.main()
