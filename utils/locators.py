### XPATHS:
from selenium.webdriver.common.by import By

##LOGIN
USERNAME_INPUT_LOCATOR = (By.XPATH, "//*[@id='identity']")

PASSWORD_INPUT_LOCATOR = (By.XPATH, "//*[@id='password']")

SUBMIT_BUTTON_LOCATOR_1 = (By.XPATH, "//form//button[@type='submit']")

SUBMIT_BUTTON_LOCATOR_2 = (By.XPATH, "//form//input[@type='submit']")

SUBMIT_BUTTON_LOCATOR_3 = (By.XPATH, "//button[contains(., 'Login')]")

SUBMIT_BUTTON_LOCATOR_4 = (By.XPATH, "//button[contains(., 'Sign in')]")

## MAIN PAGE
NAV_BAR_LOCATOR = (By.XPATH, "//*[contains(@class, 'navbar')]")

CONFIGURED_BUTTON_LOCATOR = (By.XPATH, "//*[@id='navbar-main']//a[contains(normalize-space(.), 'Configured')]")

#CONFIGURED ONUS SECTION
SEARCH_USER_TEXTBOX_LOCATOR = (By.XPATH, "//*[@id='free_text' or @name='free_text' or contains(@placeholder,'Search')]")

ROW_LOCATOR = (By.XPATH, "//tr[contains(@class, 'valign-center')]")

ONU_ROW_VIEW_BUTTON_LOCATOR = (By.XPATH, ".//a[contains(.,'View') or contains(.,'view')] | .//button[contains(.,'View') or contains(.,'view')]")


#ONU VIEW PAGE - MAIN
REVEAL_PPPOE_USERNAME_BUTTON_LOCATOR = (By.XPATH, "//a[contains(@class,'show_pppoe_username')]")

PPPOE_USERNAME_SPAN_LOCATOR = (By.XPATH, "//span[contains(@class, 'pppoe_username') and not(contains(@class, 'hidden'))]")

ONU_STATUS_LOCATOR = (By.XPATH, "//dd[@id='onu_status_wrapper']")

ONU_URL_LOCATOR = (By.XPATH, "//td[normalize-space()='URL']")

VLAN_SELECT_LOCATOR = (By.XPATH, "//select[@id='extra_vlan_id']")

DOWNSTREAM_SPEED_SELECT_LOCATOR = (By.XPATH, "//select[@id='download_speed']")

UPSTREAM_SPEED_SELECT_LOCATOR = (By.XPATH, "//select[@id='upload_speed']")

SPEED_PROFILE_CONFIGURE_BUTTON_LOCATOR = (By.XPATH, "//a[@href='#updateSpeedProfiles']")

ONU_UPDATE_MODE_BUTTON_LOCATOR = (By.XPATH, "//a[@href='#updateMode']")

ATTACHED_VLANS_BUTTON_LOCATOR = (By.XPATH, "//a[contains(@href,'#updateVlans')]")

ONU_REBOOT_BUTTON_LOCATOR = (By.XPATH, "//a[@id='rebootModal' or normalize-space(.)='Reboot']")

ONU_RESYNC_BUTTON_LOCATOR = (By.XPATH, "//a[@id='rebuildModal' or normalize-space(.)='Resync config']")

#ONU VIEW PAGE - MAIN - TR69 STATUS

TR69_STATUS_BUTTON_LOCATOR = (By.XPATH, "//button[@id='tr69_status_button']")

PPP_INTERFACE_SECTION_BUTTON_LOCATOR = (By.XPATH, "//div[@id='status_tr69']//div[@id='all_tr69_pannels']//div[contains(@class,'panel-heading') and contains(@data-groupname,'PPP Interface')]")

CONECTION_STATUS_SPAN_LOCATOR = (By.XPATH, "//td[normalize-space()='Connection status']/following-sibling::td//span")

RESET_PPP_CONECTION_SELECTOR_LOCATOR = (By.XPATH,"//td[normalize-space()='Reset connection']/following-sibling::td//select")

PPP_GATEWAY_LOCATOR = (By.XPATH, "//td[normalize-space()='PPP Gateway']/following-sibling::td")

#MODALS
GENERAL_MODAL_LOCATOR_1 = (By.XPATH, "//div[contains(@class,'modal') and not(contains(@style,'display: none'))]")

SPEED_PROFILE_CONFIGURE_MODAL_LOCATOR = (By.XPATH, "//div[contains(@class,'modal') and @id='updateSpeedProfiles']")

ONU_UPDATE_MODE_MODAL_LOCATOR = (By.XPATH, "//div[contains(@class,'modal') and @id='updateMode']")

RESYNC_MODAL_LOCATOR = (By.XPATH, "//div[@id='rebuildModal' and contains(@class,'in')]")

REBOOT_MODAL_LOCATOR = (By.XPATH, "//div[@id='rebootModal' and contains(@class,'in')]")

OK_MODAL_BUTTON_LOCATOR_1 = (By.XPATH,"//div[@class='messagebox_buttons']//button[@class='messagebox_button_done']")

SVLAN_CONTROLS_WRAPPER_LOCATOR = (By.XPATH, "//div[@id='svlan_controls_wrapper']")

SVLAN_CHECK_BOX_LOCATOR = (By.XPATH, "//input[@id='use_svlan' and @type='checkbox']")

SUBMIT_UPDATE_SPEED_PROFILES_BUTTON_LOCATOR = (By.XPATH, "//a[@id='submitUpdateSpeedProfiles' or contains(@class,'submitUpdateSpeedProfiles') or normalize-space(.)='Save']")

SUBMIT_UPDATE_MODE_BUTTON_LOCATOR = (By.ID, "submitUpdateMode")

CONFIRM_RESYNC_BUTTON_LOCATOR = (By.XPATH, "//div[@id='rebuildModal']//a[contains(normalize-space(),'Resync config') and contains(@class,'btn-yellow')]")

CONFIRM_REBOOT_BUTTON_LOCATOR = (By.XPATH, "//div[@id='rebootModal']//a[contains(normalize-space(),'Reboot') and contains(@class,'btn-warning')]")

#TABLES
GENERIC_TABLE_LOCATOR_1 = (By.XPATH, "//table[contains(@class,'table')]")
