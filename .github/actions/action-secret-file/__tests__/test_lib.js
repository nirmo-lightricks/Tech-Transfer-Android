const fs = require("fs").promises
const lib  = require("../lib")

test('get file path respects existing file', async () => {
    const filePath = await lib.getFilePath("x")
    expect(filePath).toBe("x");
  });


  test('get file path null create new file name', async () => {
    const filePath = await lib.getFilePath(null)
    await fs.access(filePath)
    await fs.unlink(filePath)
  });

  test('write text file', async()=> {
      const filePath = "foo";
      const secret = "great secret";
      await lib.writeSecretToFile("text", secret , filePath)
      const fileValue = await fs.readFile(filePath,"utf-8")
      expect(fileValue).toBe(secret);
      await fs.unlink(filePath)
  });

  test('write base64 file', async()=> {
    const filePath = "foo";
    const secret = "great secret";
    const base64Secret = "Z3JlYXQgc2VjcmV0"
    await lib.writeSecretToFile("base64", base64Secret , filePath)
    const fileValue = await fs.readFile(filePath,"utf-8")
    expect(fileValue).toBe(secret);
    await fs.unlink(filePath)
});