import inspect
import app.epaper.main as epaper_main


def main():
    app_class = None

    for _, obj in inspect.getmembers(epaper_main, inspect.isclass):
        if hasattr(obj, "render_sleep_screen") and hasattr(obj, "paste_home_art"):
            app_class = obj
            break

    if app_class is None:
        raise RuntimeError("Could not find the e-paper app class with render_sleep_screen().")

    app = app_class()
    image = app.render_sleep_screen()
    app.display.full_refresh(image)
    app.display.sleep()


if __name__ == "__main__":
    main()
