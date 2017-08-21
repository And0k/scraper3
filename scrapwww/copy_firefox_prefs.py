'''
When I try to automate login on an unsafe page, the firefox opens a new tab
"https://support.mozilla.org/1/firefox/53.0.2/WINNT/pt-PT/insecure-password".
How can I disable this? I think that property
"security.insecure_field_warning.contextual.enabled" is related to this behavior but
i don't know how i could disable it by python code.

From the version 0.11 of geckodriver is possible to change firefox preferences by the
moz:firefoxOptions capability instead of change profile settings:

{
    "capabilities": {
        "alwaysMatch": {
            "moz:firefoxOptions": {
                "binary": "/usr/local/firefox/bin/firefox",
                "args": ["--no-remote"],
                "prefs": {
                    "dom.ipc.processCount": 8
                },
                "log": {
                    "level": "trace"
                }
            }
        }
    }
}

'''
def get_cap(path_drivers):
    #In this way i was able to change the
    # "security.insecure_field_warning.contextual.enabled" with this solution:

    firefox_driver = path_drivers + "geckodriver.exe"
    firefox_capabilities = DesiredCapabilities.FIREFOX.copy()
    #To disable insecure-password tab by support firefox
    firefox_options = { "moz:firefoxOptions" : { "prefs" : { "security.insecure_field_warning.contextual.enabled" : False } } }
    firefox_capabilities["alwaysMatch"] = firefox_options
    return webdriver.Firefox(executable_path=firefox_driver, \
                             capabilities=firefox_capabilities)


#simpler solution:

from selenium.webdriver import Firefox, FirefoxProfile

profile = FirefoxProfile()
profile.set_preference('security.insecure_field_warning.contextual.enabled', False)
profile.set_preference('security.insecure_password.ui.enabled', False)
driver = Firefox(firefox_profile=profile)