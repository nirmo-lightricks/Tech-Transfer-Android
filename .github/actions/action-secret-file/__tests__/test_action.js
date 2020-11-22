const action = require('../action')
const fs = require("fs").promises;

test('test cleanup', async () => {
    process.env['STATE_isPost'] = "true"
    const filePath =  "foo"
    await fs.writeFile(filePath, "foofoo")
    core = {
        getState: createKeyedFunction({"file_path": filePath})
    }
    await action(core,{})
    await expect(fs.access(filePath)).rejects.toThrow(`ENOENT: no such file or directory, access '${filePath}'`)
    delete process.env['STATE_isPost']
  });

test('invalid secret type', async() => {
    core = {
        getInput: createKeyedFunction({"type": "invalid foo"}),
        setFailed: jest.fn()
    }
    await action(core,{})
    expect(core.setFailed.mock.calls[0][0]).toBe("type needs to be either base64 or text");
});  


test('file action', async() => {
    var lib = {
        getFilePath: jest.fn(),
        writeSecretToFile: jest.fn()
    };
    const fileName = "file1";
    const secret = "secret1";
    const secretType = "text"
    lib.getFilePath.mockReturnValueOnce(fileName);
    
    core = {
        getInput: createKeyedFunction({
            "type": secretType,
            "secret":secret,
            "file_path":fileName
        }),
        setOutput: jest.fn(),
        saveState: jest.fn()
    }
    await action(core,lib)
    expect(lib.getFilePath.mock.calls[0][0]).toBe(fileName)
    expect(lib.writeSecretToFile.mock.calls[0]).toEqual([secretType, secret, fileName])
    expect(core.setOutput.mock.calls[0]).toEqual(["file_path", fileName]);
    expect(core.saveState.mock.calls[0]).toEqual(["file_path", fileName]);
});

  function createKeyedFunction(input){
      return (key)=> {
          if(key in input){
              return input[key];
          }
          console.log(input)
          throw  new Error(`key ${key} does not exist`); 
      }
  }