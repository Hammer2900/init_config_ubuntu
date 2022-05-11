#!/run/media/izot/652aebd5-b153-4f9e-ba3d-2fb1b4d4b246/jek/TEMP/all_python/.venv_f/bin/python
import fire
import os


class Vpn:
    def show(self):
        os.system("""sakura -e 'fish -C "nmcli con"'""")

    def list(self):
        os.system('nmcli con')

    def enable_aws(self, notify=True):
        os.system('nmcli con up id somo_hammer2900_somo')
        self.list()
        if notify:
            os.system('notify-send "VPN" "enable AWS vpn"')

    def enable_wg(self, notify=True):
        os.system('nmcli con up id hammer')
        self.list()
        if notify:
            os.system('notify-send "VPN" "enable WG vpn"')

    def disable_all(self, log=True, notify=True):
        if log:
            self.list()
        os.system('nmcli con down id hammer')
        os.system('nmcli con down id somo_hammer2900_somo')
        if log:
            self.list()
        if notify:
            os.system('notify-send "VPN" "disable all"')


if __name__ == '__main__':
    fire.Fire(Vpn)
