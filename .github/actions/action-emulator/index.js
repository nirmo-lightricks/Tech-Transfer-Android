const core = require('@actions/core');
const exec = require('@actions/exec');
const IsPost = !!process.env['STATE_isPost']

try {
    if (IsPost) {
        await terminateEmulator()
    }
    else {
        await runEmulator()
    }

} catch (error) {
    core.setFailed(error.message);
}

async function runEmulator() {
    const version = core.getInput("version")
    if(!isNumeric(version)){
        throw new Error(`version needs to be numeric but is ${version}`)
    }
    const creationCommand = `echo no | avdmanager create avd -n android${version} -k 'system-images;android-${version};default;x86' --force`
    const creationBashCommand = `/bin/bash -c "${creationCommand}"`
    console.log(creationBashCommand)
    await exec.exec(creationCommand)
    await exec.exec("emulator -list-avds")
    await exec.exec(`emulator -gpu swiftshader_indirect -no-window -feature GLESDynamicVersion -avd android${version} -memory 2048 -partition-size 2048 -cache-size 2048 >/dev/null 2>&1 &`)
}

async function terminateEmulator() {
    process.env["ADB_HOME"]=process.env["ANDROID_HOME"] + "/platform-tools"
    await exec.exec("python3 tools/jenkins/terminate_emulators.py")
}

function isNumeric(str) {
    if (typeof str != "string") return false // we only process strings!  
    return !isNaN(str) && // use type coercion to parse the _entirety_ of the string (`parseFloat` alone does not do this)...
           !isNaN(parseFloat(str)) // ...and ensure strings of whitespace fail
  }