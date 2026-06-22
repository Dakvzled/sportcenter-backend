*** Settings ***
Library    SeleniumLibrary

*** Test Cases ***
Buka Halaman Web Frontend
    Evaluate    webdriver_manager.chrome.ChromeDriverManager().install()    modules=webdriver_manager.chrome
    Open Browser    http://localhost:5173    chrome
    Maximize Browser Window
    Sleep    2s

Skenario Login
    Click Element    //*[@id="root"]/div/nav/div/div[1]/div[2]/button[3]
    Sleep    5s
    Wait Until Element Is Visible    //*[@id="root"]/div/div[2]/div/div[1]/form/div[1]/div/input    timeout=10s
    
    # Skenario invalid email input
    Input Text    //*[@id="root"]/div/div[2]/div/div[1]/form/div[1]/div/input    wargasolo
    Sleep    2s
    Click Button    //*[@id="root"]/div/div[2]/div/div[1]/form/button
    Sleep    2s
    Clear Element Text    //*[@id="root"]/div/div[2]/div/div[1]/form/div[1]/div/input
    Input Text    //*[@id="root"]/div/div[2]/div/div[1]/form/div[1]/div/input    wargasolo@gmail.com
    Sleep    2s
    Clear Element Text    //*[@id="root"]/div/div[2]/div/div[1]/form/div[2]/div/input
    Input Text    //*[@id="root"]/div/div[2]/div/div[1]/form/div[2]/div/input    wargasolobiasa
    Click Button    //*[@id="root"]/div/div[2]/div/div[1]/form/button
    Sleep    2s    

Skenario Proses Booking
    Click Button    //*[@id="root"]/div/nav/div/div/div[2]/button[2]
    Sleep    3s
    Click Button    //*[@id="root"]/div/div/div/div/div[1]/div/div[1]/div[1]/div/button[2]
    Sleep    2s
    Click Element    //*[@id="root"]/div/div/div/div/div[1]/div/div[1]/div[2]/input
    Sleep    2s
    Click Button    //*[@id="root"]/div/div/div/div/div[2]/div/div[2]/button[14]
    Click Button    //*[@id="root"]/div/div/div/div/div[2]/div/div[2]/button[15]
    Sleep    3s
    Scroll Element Into View    //*[@id="root"]/div/div/div/div/div[2]/div/div[3]/button
    Wait Until Element Is Visible    //*[@id="root"]/div/div/div/div/div[2]/div/div[3]/button    timeout=5s
    Click Button    //*[@id="root"]/div/div/div/div/div[2]/div/div[3]/button 
    Handle Alert    ACCEPT
    
    Wait Until Page Contains Element    //*[@id="root"]/div/nav/div/div/div[2]/button[3]    timeout=10s
    
    # Eksekusi Upload File
    Wait Until Page Contains Element    xpath=//input[@type='file']    timeout=5s
    Choose File    xpath=//input[@type='file']    C:/Users/Lenovo/OneDrive/Pictures/Screenshots/Screenshot 2026-06-07 061737.png
    Sleep    3s