const fs = require("fs").promises;

module.exports = async (core, lib) => {
    try {
        const IsPost = core.getState("isPost")
        if (IsPost) {
            await runCleanup(core)
        }
        else {
            //This is needed for identifying the post action
            core.saveState("isPost", true)
            await runAction(core, lib)
        }
    
    } catch (error) {
        core.setFailed(error.message);
    }
}

async function runCleanup(core) {
    const path = core.getState('file_path')
    await fs.unlink(path)
}

async function runAction(core, lib) {
    const secretType = core.getInput("type", { required: true });
    if (secretType != "text" && secretType != "base64") {
        throw new Error("type needs to be either base64 or text");
    }
    const secret = core.getInput("secret", { required: true })
    const inputFilePath = core.getInput("file_path")
    const filePath = lib.getFilePath(inputFilePath)
    lib.writeSecretToFile(secretType, secret, filePath)
    core.setOutput("file_path", filePath)
    core.saveState("file_path", filePath)
    
}
