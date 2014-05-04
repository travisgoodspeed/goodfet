#!/usr/bin/env python
# GoodFET Client Library

import sys;
import binascii;

from GoodFET import GoodFET;

class GoodFETSLC2(GoodFET):
	"""GoodFET variant for the Silicon lab C2 protocol"""
	APP=0x06;
	
	def setup(self):
		"""Setup the SLC2 protocol"""
		self.writecmd(0x06, 0x10, 0);

	def reset(self):
		self.writecmd(0x06, 0x84, 0);
		
	def peekblock(self, addr, len):
		"""Grab block from FLASH at address addr"""
		dat= [addr&0xFF, (addr&0xFF00)>>8];
		self.writecmd(0x06, 0x02, 2, dat);
		return self.data;
		
	def pokeblock(self, addr, len, data):
		d = [len, data];
		self.writecmd(0x06, 0x03, len, d);
		
	def getdevid(self):
		return self.writecmd(0x06, 0x80, 0, []);
	
	def getrevid(self):
		return self.writecmd(0x06, 0x81, 0, []);
		
	def page_erase(self, addr):
		self.writecmd(0x06, 0x82, 1, addr);
	
	def device_erase(self):
		self.writecmd(0x06, 0x83, 0, []);
