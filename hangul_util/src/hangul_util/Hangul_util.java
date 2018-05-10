package hangul_util;
import java.util.List;
import java.io.File;
import java.io.FileInputStream;
import java.io.InputStreamReader;
import java.io.FileWriter;
import java.io.FileNotFoundException;
import java.io.BufferedReader;
import java.io.IOException;
import scala.collection.Seq;
import org.openkoreantext.processor.OpenKoreanTextProcessorJava;
import org.openkoreantext.processor.phrase_extractor.KoreanPhraseExtractor;
import org.openkoreantext.processor.tokenizer.KoreanTokenizer;
/*
  <dependencies>
<dependency>
    <groupId>org.openkoreantext</groupId>
    <artifactId>open-korean-text</artifactId>
    <version>2.2.0</version>
</dependency>
</dependencies>
 */
public class Hangul_util {

	 public static void main(String args[]) {
	      
		 String str = new String();
		 str = "";
	      for(int x = 1; x<2; x++) {
	      File file  = new File("C:\\Users\\yeunkun\\.spyder-py3\\rnn2\\all\\corpus ("+x+").txt");
	      try {
	      BufferedReader bufreader = new BufferedReader(new InputStreamReader(new FileInputStream(file), "UTF-8"));
	     
	      String line = "";
	      while((line = bufreader.readLine()) != null) {

		      CharSequence normalized = OpenKoreanTextProcessorJava.normalize(line);
		      Seq<KoreanTokenizer.KoreanToken> tokens = OpenKoreanTextProcessorJava.tokenize(normalized);
		      List<KoreanPhraseExtractor.KoreanPhrase> phrases = OpenKoreanTextProcessorJava.extractPhrases(tokens, false, false);
		      
		      for(KoreanPhraseExtractor.KoreanPhrase p : phrases)
		    	  str = str+" "+p.text();
		       str = str+"\n";
	    	 
	      }
	      
	      bufreader.close();
	      
	      }catch(FileNotFoundException e) {
	      ;
	      }catch(IOException e) {
	         ;
	         
	      }

      
	      try {
	      File newfile  = new File("C:\\Users\\yeunkun\\.spyder-py3\\rnn2\\all\\new.txt");
	      FileWriter filewriter = new FileWriter(newfile);
	      System.out.println("start");
	      filewriter.write(str);
	      System.out.println("end");
	      filewriter.close();
	      }
	      catch(IOException e){
	    	  
	      }
	   }
	      
	      
	   }

	
}
