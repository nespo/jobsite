#!/usr/bin/env node

'use strict'

const path = require('path')
const fs = require('fs')
const picocolors = require('picocolors')
const postcss = require('postcss')
const rtlcss = require('../lib/rtlcss.js')
const configLoader = require('../lib/config-loader.js')
const { version, bugs } = require('../package.json')

const HELP_TEXT = `Usage: rtlcss [option option=parameter ...] [source] [destination]

Option           Description
--------------   ----------------------------------------------
-h,--help        Print help (this message) and exit.
-v,--version     Print version number and exit.
-c,--config      Path to configuration settings file.
- ,--stdin       Read from stdin stream.
-d,--directory   Process all *.css files from input directory (recursive).
-e,--ext         Used with -d option to set the output files extension.
                 Default: ".rtl.css".
-s,--silent      Silent mode, no warnings or errors are printed.

*If no destination is specified, output will be written to the same input folder as {source}.rtl.{ext}
`

let input, output, directory, ext, config, currentErrorcode, arg
const args = process.argv.slice(2)
let shouldBreak = false

process.on('exit', () => { process.reallyExit(currentErrorcode) })

function printWarning (...args) {
  console.warn(picocolors.yellow(...args))
}

function printInfo (...args) {
  console.info(picocolors.green(...args))
}

function printError (...args) {
  console.error(picocolors.red(...args))
}

function printHelp () {
  console.log(HELP_TEXT)

  printInfo(`RTLCSS version: ${version}`)
  printInfo(`Report issues to: ${bugs.url}`)
}

while ((arg = args.shift())) {
  switch (arg) {
    case '-h':
    case '--help':
      printHelp()
      shouldBreak = true
      break
    case '-v':
    case '--version':
      printInfo(`rtlcss version: ${version}`)
      shouldBreak = true
      break
    case '-c':
    case '--config':
      arg = args.shift()
      try {
        config = configLoader.load(path.resolve(arg))
      } catch (e) {
        printError('rtlcss: invalid config file. ', e)
        shouldBreak = true
        currentErrorcode = 1
      }
      break
    case '-d':
    case '--directory':
      directory = true
      break
    case '-e':
    case '--ext':
      ext = args.shift()
      break
    case '-s':
    case '--silent':
      console.log = console.info = console.warn = () => {}
      break
    case '-':
    case '--stdin':
      input = '-'
      break
    default:
      if (arg[0] === '-') {
        printError(`rtlcss: unknown option. ${arg}`)
        shouldBreak = true
      } else if (!input) {
        input = path.resolve(arg)
      } else if (!output) {
        output = path.resolve(arg)
      }
      break
  }
}

if (!shouldBreak) {
  if (!directory && !input) {
    printError('rtlcss: no input file')
    console.log('')
    printHelp()
    shouldBreak = true
  }
  if (!config && input !== '-') {
    try {
      let cwd = input
      if (directory !== true) {
        cwd = path.dirname(input)
      }
      config = configLoader.load(null, cwd)
    } catch (e) {
      printError('rtlcss: invalid config file. ', e)
      currentErrorcode = 1
      shouldBreak = true
    }
  }
}

if (!shouldBreak) {
  if (!output && input !== '-') {
    if (directory !== true) {
      const extension = path.extname(input)
      output = extension ? input.replace(extension, `.rtl${extension}`) : `${input}.rtl`
    } else {
      output = input
    }
  }

  const processCSSFile = (error, data, outputName) => {
    if (error) {
      printError(`rtlcss: ${error.message}`)
      return
    }

    let result
    const opt = { map: false }

    if (input !== '-') {
      opt.from = input
      opt.to = output
    }

    if (!config) {
      printWarning('rtlcss: Warning! No config present, using defaults.')
      result = postcss([rtlcss]).process(data, opt)
    } else {
      if ('map' in config === true && input !== '-') {
        opt.map = config.map
      }

      result = postcss([rtlcss.configure(config)]).process(data, opt)
    }

    if (output) {
      let savePath = outputName
      if (directory !== true) {
        savePath = output
      }

      printInfo('Saving:', savePath)

      fs.writeFile(savePath, result.css, (err) => {
        if (err) printError(err)
      })

      if (result.map) {
        fs.writeFile(`${savePath}.map`, result.map, (err) => {
          if (err) printError(err)
        })
      }
    } else {
      process.stdout.write(`${result.css}\n`)
    }
  }

  const walk = (dir, done) => {
    fs.readdir(dir, (error, list) => {
      if (error) {
        return done(error)
      }

      let i = 0;
      (function next () {
        let file = list[i++]
        if (!file) {
          return done(null)
        }

        file = dir + path.sep + file
        fs.stat(file, (err, stat) => {
          if (err) {
            printError(err)
          } else if (stat && stat.isDirectory()) {
            walk(file, (err) => {
              if (err) {
                printError(err)
              } else {
                next()
              }
            })
          } else {
            // process only *.css files
            if (file.endsWith('.css')) {
              // compute output directory
              const relativePath = path.relative(input, file).split(path.sep)
              relativePath.pop()
              relativePath.push(path.basename(file).replace('.css', ext || '.rtl.css'))

              // set rtl filename
              const rtlFile = path.join(output, relativePath.join(path.sep))

              // create output directory if it does not exist
              const dirName = path.dirname(rtlFile)
              if (!fs.existsSync(dirName)) {
                fs.mkdirSync(dirName, { recursive: true })
              }

              // read and process the file.
              fs.readFile(file, 'utf8', (e, data) => {
                try {
                  processCSSFile(e, data, rtlFile)
                } catch (e) {
                  printError('rtlcss: error processing file', file)
                  printError(e)
                }
              })
            }

            next()
          }
        })
      })()
    })
  }

  if (input !== '-') {
    if (directory !== true) {
      fs.stat(input, (error, stat) => {
        if (error) {
          printError(error)
        } else if (stat && stat.isDirectory()) {
          printError('rtlcss: Input expected to be a file, use the -d option to process a directory.')
        } else {
          fs.readFile(input, 'utf8', (e, data) => {
            try {
              processCSSFile(e, data)
            } catch (e) {
              printError('rtlcss: error processing file', input)
              printError(e)
            }
          })
        }
      })
    } else {
      walk(input, (error) => {
        if (error) {
          printError(`rtlcss: ${error}`)
        }
      })
    }
  } else {
    process.stdin.resume()
    process.stdin.setEncoding('utf8')

    let buffer = ''
    process.stdin.on('data', (data) => {
      buffer += data
    })
    process.on('SIGINT', () => {
      processCSSFile(false, buffer)
      process.exit()
    })
    process.stdin.on('end', () => {
      processCSSFile(false, buffer)
    })
  }
}
