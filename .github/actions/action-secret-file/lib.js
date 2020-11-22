const fs = require("fs").promises;
const tmp = require("tmp-promise");

exports.getFilePath = async (inputFilePath) =>{
    if (inputFilePath) {
        return inputFilePath
    }
    const {path} = await tmp.file();
    return path
}

exports.writeSecretToFile =  async (secretType, secret, filePath) => {
    if (secretType == "text") {
        await fs.writeFile(filePath, secret)
    }
    else {
        const buff = Buffer.from(secret, 'base64');
        await fs.writeFile(filePath, buff);
    }
}


