package scraper;

import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;
import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.concurrent.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class MyScraper {

	// Constants for base URL, output directory, timeout, and threading parameters
	private static final String BASE_URL = "https://papers.nips.cc";
	private static final String OUTPUT_DIR = "D:/Data Science/Scraped_Data-Using_Java/"; // Base output directory
	private static final int TIMEOUT = 30000; // Timeout for HTTP requests
	private static final int THREAD_COUNT = 100; // Number of threads for concurrent scraping
	private static final int RETRY_LIMIT = 3; // Retry limit for failed connections
	private static final int START_YEAR = 2018; // Starting year for scraping papers
	private static final int END_YEAR = 2019; // Ending year for scraping papers

	// Main entry point: fetches the main page, extracts year links, and triggers further processing
	public static void main(String[] args) {
		ExecutorService executor = Executors.newFixedThreadPool(THREAD_COUNT);
		try {
			Document mainPage = Jsoup.connect(BASE_URL).timeout(TIMEOUT).get();
			Elements yearLinks = mainPage.select("a[href^=/paper_files/paper/]");

			// Process each year link within the specified range (2019–2023)
			for (Element yearLink : yearLinks) {
				String yearText = yearLink.text();
				Integer year = extractYear(yearText);

				if (year != null && year >= START_YEAR && year <= END_YEAR) {
					String yearUrl = BASE_URL + yearLink.attr("href");
					executor.submit(() -> processYear(yearUrl, year));
				}
			}
		} catch (IOException e) {
			System.err.println("Failed to connect to main page: " + e.getMessage());
		}
		executor.shutdown();
	}

	// Extracts the year from a string using regex
	private static Integer extractYear(String text) {
		Pattern pattern = Pattern.compile("(\\d{4})");
		Matcher matcher = pattern.matcher(text);
		if (matcher.find()) {
			return Integer.parseInt(matcher.group(1));
		}
		return null; // Return null if no valid year is found
	}

	// Processes the year page to extract paper links and submit them for further processing
	private static void processYear(String yearUrl, int year) {
		try {
			Document yearPage = Jsoup.connect(yearUrl).timeout(TIMEOUT).get();
			Elements paperLinks = yearPage.select("ul.paper-list li a[href$=Abstract-Conference.html]");
			for (Element paperLink : paperLinks) {
				String paperUrl = BASE_URL + paperLink.attr("href");
				processPaper(paperUrl, year);
			}
		} catch (IOException e) {
			System.err.println("Failed to process year page: " + e.getMessage());
		}
	}

	// Processes each paper page to find and download the PDF link
	private static void processPaper(String paperUrl, int year) {
		try {
			Document paperPage = Jsoup.connect(paperUrl).timeout(TIMEOUT).get();
			Element pdfLink = paperPage.selectFirst("a[href$=Paper-Conference.pdf]");
			if (pdfLink != null) {
				String pdfUrl = BASE_URL + pdfLink.attr("href");
				downloadPDF(pdfUrl, year);
			}
		} catch (IOException e) {
			System.err.println("Failed to process paper page: " + e.getMessage());
		}
	}

	// Downloads the PDF from the given URL and saves it in the appropriate year folder
	private static void downloadPDF(String pdfUrl, int year) {
		String fileName = pdfUrl.substring(pdfUrl.lastIndexOf('/') + 1);

		// Create year-specific directory
		String yearDir = OUTPUT_DIR + year + "/";
		try {
			Files.createDirectories(Paths.get(yearDir)); // Ensure year folder exists

			// Download the PDF
			URL url = new URL(pdfUrl);
			HttpURLConnection connection = (HttpURLConnection) url.openConnection();
			connection.setRequestMethod("GET");
			connection.setConnectTimeout(TIMEOUT);
			connection.setReadTimeout(TIMEOUT);

			try (InputStream inputStream = connection.getInputStream();
					FileOutputStream outputStream = new FileOutputStream(yearDir + fileName)) {
				byte[] buffer = new byte[8192];
				int bytesRead;
				while ((bytesRead = inputStream.read(buffer)) != -1) {
					outputStream.write(buffer, 0, bytesRead);
				}
			}
			System.out.println("Downloaded: " + fileName + " to " + yearDir);
		} catch (IOException e) {
			System.err.println("Failed to download PDF: " + e.getMessage());
		}
	}
}
