const core = require('@actions/core');
const util = require('util');
const exec = util.promisify(require('child_process').exec);

async function runEmulator() {
    const version = core.getInput("version")
    if(!isNumeric(version)){
        throw new Error(`version needs to be numeric but is ${version}`)
    }
    const creationCommand = `echo no | avdmanager create avd -n android${version} -k 'system-images;android-${version};default;x86' --force`
    console.log(creationCommand)
    await exec(creationCommand)
    console.log(await exec("emulator -list-avds"))
    const emulatorCommand = `emulator -gpu swiftshader_indirect -no-window -feature GLESDynamicVersion -avd android${version} -memory 3072 -partition-size 2048 -cache-size 2048 >/dev/null 2>&1 &`
    console.log(emulatorCommand)
    await exec(emulatorCommand)
}

async function terminateEmulator() {
    process.env["ADB_HOME"]=process.env["ANDROID_HOME"] + "/platform-tools"
    console.log("terminating emulator")
    const { stdout, stderr } = await exec("python3 tools/jenkins/terminate_emulators.py")
    console.log(stdout)
    console.log(stderr)

}

function isNumeric(str) {
    if (typeof str != "string") return false // we only process strings!
    return !isNaN(str) && // use type coercion to parse the _entirety_ of the string (`parseFloat` alone does not do this)...
           !isNaN(parseFloat(str)) // ...and ensure strings of whitespace fail
  }

  async function run () {
    try {
        await runEmulator()

    } catch (error) {
        core.setFailed(error.message);
    }
}

run()