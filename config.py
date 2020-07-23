JS_PORT = '''
function a(para1, para2) {
  eval(`${para1}r=''+${para2}`)
  return r
}
'''
