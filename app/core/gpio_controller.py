class HardwareButtonController:
    def __init__(self, app):
        from gpiozero import Button

        self.app = app

        self.buttons = {
            "up": Button(17, pull_up=True, bounce_time=0.08),
            "down": Button(27, pull_up=True, bounce_time=0.08),
            "select": Button(22, pull_up=True, bounce_time=0.08),
            "back": Button(23, pull_up=True, bounce_time=0.08),
        }

        for action, button in self.buttons.items():
            button.when_pressed = lambda a=action: self.send_action(a)

    def send_action(self, action):
        self.app.after(0, lambda: self.app.handle_hardware_button(action))
