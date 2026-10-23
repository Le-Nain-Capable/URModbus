"""Command-line runner for the optimization program."""

import argparse
from URModbus.config.constants import Settings
from URModbus.config.parser import parse_Settings


from time import sleep

def main():
    parser = argparse.ArgumentParser(description="URModbus")
    # Add arguments for every attribute in the Settings class
    setting_names = [
        attr
        for attr in dir(Settings)
        if not callable(getattr(Settings, attr))
        and not attr.startswith("_")
    ]

    SETTINGS_META = parse_Settings()

    for setting_name, meta in SETTINGS_META.items():

        help_text = meta["description"]

        if "default" in meta:
            help_text += f" (default: {meta['default']})"

        parser.add_argument(
            f"--{setting_name}",
            type=str,
            default=None,   # ne modifie rien si l'option n'est pas passée
            help=help_text,
        )
   
    args = parser.parse_args()
    update_result = []
    # Process arguments and update settings if they are provided (not None)
    for key in vars(args):
        value = getattr(args, key)
        if value is not None:
            result,text = Settings.updateSetting(key, value)
            update_result.append([key,result,text])

    if update_result != []:
        print("# ---------- Running Whith custom settings ---------- #")
        for key,result,text in update_result:
            if result is False:
                print(f"{key} ignored - {text}")
            else:
                print(f"{key} accepted - {text}")
        print("# ---------------- Starting in 5 sec ---------------- #")
        sleep(5)

    from URModbus.app.main import run
    run()

if __name__ == "__main__":
    main()