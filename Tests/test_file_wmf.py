from PIL import Image, WmfImagePlugin

from .helper import PillowTestCase, hopper


class TestFileWmf(PillowTestCase):
    def test_load_raw(self):

        # Test basic EMF open and rendering
        with Image.open("Tests/images/drawing.emf") as im:
            if hasattr(Image.core, "drawwmf"):
                # Currently, support for WMF/EMF is Windows-only
                im.load()
                # Compare to reference rendering
                imref = Image.open("Tests/images/drawing_emf_ref.png")
                imref.load()
                self.assert_image_similar(im, imref, 0)

        # Test basic WMF open and rendering
        with Image.open("Tests/images/drawing.wmf") as im:
            if hasattr(Image.core, "drawwmf"):
                # Currently, support for WMF/EMF is Windows-only
                im.load()
                # Compare to reference rendering
                imref = Image.open("Tests/images/drawing_wmf_ref.png")
                imref.load()
                self.assert_image_similar(im, imref, 2.0)

    def test_register_handler(self):
        class TestHandler:
            methodCalled = False

            def save(self, im, fp, filename):
                self.methodCalled = True

        handler = TestHandler()
        WmfImagePlugin.register_handler(handler)

        im = hopper()
        tmpfile = self.tempfile("temp.wmf")
        im.save(tmpfile)
        self.assertTrue(handler.methodCalled)

        # Restore the state before this test
        WmfImagePlugin.register_handler(None)

    def test_load_dpi_rounding(self):
        # Round up
        with Image.open("Tests/images/drawing.emf") as im:
            self.assertEqual(im.info["dpi"], 1424)

        # Round down
        with Image.open("Tests/images/drawing_roundDown.emf") as im:
            self.assertEqual(im.info["dpi"], 1426)

    def test_save(self):
        im = hopper()

        for ext in [".wmf", ".emf"]:
            tmpfile = self.tempfile("temp" + ext)
            self.assertRaises(IOError, im.save, tmpfile)
