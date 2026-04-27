import argparse
from URModbus.config.constants import Settings
from time import sleep

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="URModbus")
    # Add arguments for every attribute in the Settings class
    for attr_name in dir(Settings):
        # Skip private/internal attributes and non-settings constants if necessary,
        # but for simplicity, we'll add an argument for everything found.
        if not callable(getattr(Settings, attr_name)) and '__' not in attr_name:
            parser.add_argument(f'--{attr_name}', type=str, help=f'Setting value for {attr_name}.')
   
   
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