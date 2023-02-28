const core = require('@actions/core');
const util = require('util');
const exec = util.promisify(require('child_process').exec);

async function terminateEmulator() {
    process.env["ADB_HOME"]=process.env["ANDROID_HOME"] + "/platform-tools"
    console.log("terminating emulator")
    const { stdout, stderr } = await exec("python3 tools/jenkins/terminate_emulators.py")
    console.log(stdout)
    console.log(stderr)

}

async function run () {
    try {
        await terminateEmulator()
    } catch (error) {
        core.setFailed(error.message);
    }
}

run()