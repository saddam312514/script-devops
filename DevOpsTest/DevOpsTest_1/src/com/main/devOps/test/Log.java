package com.main.devOps.test;

import java.io.File;
import java.io.IOException;
import java.util.logging.Logger;
import java.util.logging.SimpleFormatter;
import java.util.logging.FileHandler;
public class Log {
	
	
	Logger logger;
	FileHandler fh;
	
	public Log(String fileName) throws IOException {
		File f = new File(fileName);
		if(!f.exists()){
			f.createNewFile();
		}
		
		fh = new FileHandler(fileName, true);
		logger = Logger.getLogger("test");
		logger.addHandler(fh);
		SimpleFormatter formatter = new SimpleFormatter();
		fh.setFormatter(formatter);
	}

}
