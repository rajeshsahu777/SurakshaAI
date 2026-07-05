#!/usr/bin/env node //dont remove this line otherwiuse this wont work it is important line
const { Command } = require('commander');
const program = new Command();
program
  .name('catalyst')
  .description('Catalyst CLI tool for SurakshaAI')
  .version('1.0.0');
program
  .command('risk <district>')
  .description('Show risk data for a district')
  .action((district) => require('../commands/risk')(district));
program.parse()