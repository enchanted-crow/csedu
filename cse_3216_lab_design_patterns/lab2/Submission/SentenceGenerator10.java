import java.util.Collections;
import java.util.ArrayList;
import java.util.concurrent.ThreadLocalRandom;
import java.util.Scanner;

/**
 * Randomizer class
 * Used for randomly picking words from an arraylist of string
 */
abstract class Randomizer {
    public static final int REPEAT_MAX = 3;

    // Returns a random integer in a range
    public static int randomInt(int a, int b) {
        return ThreadLocalRandom.current().nextInt(a, b + 1);
    }

    // Randomly pick a few words from the array
    public static ArrayList<String> randomWordPicker(ArrayList<String> arr) {
        ArrayList<String> picked = new ArrayList<String>();
        for (String word : arr) {
            int num = randomInt(1, REPEAT_MAX);
            for (int i = 0; i < num; i++) {
                picked.add(word);
            }
        }
        return picked;
    }
}

/**
 * Sentence Generator Class
 */
class SentenceGenerator {
    private IWordAdder wordAdder;
    private IWordGenerator wordGenerator;
    public ArrayList<String> vocabulary;

    public SentenceGenerator(IWordAdder _wordAdder, IWordGenerator _wordGenerator) {
        vocabulary = new ArrayList<String>();
        wordAdder = _wordAdder;
        wordGenerator = _wordGenerator;
    }

    // Implement adding a word to the vocabulary
    public void addWord(String word) {
        vocabulary = wordAdder.addWord(vocabulary, word);
    }

    // Implement sentence generation
    public String generateWord() {
        return wordGenerator.generateWord(vocabulary);
    }
}

/**
 * IWordAdder
 */
interface IWordAdder {
    // Implement adding a word to the vocabulary
    public ArrayList<String> addWord(ArrayList<String> vocabulary, String word);
}

/**
 * WordAdderLower
 * - Used by Random Sentence Generator and Sorted Sentence Generator
 */
class WordAdderLower implements IWordAdder {
    public ArrayList<String> addWord(ArrayList<String> vocabulary, String word) {
        vocabulary.add(word.toLowerCase());
        return vocabulary;
    }
}

/**
 * WordAdderUpperReverse
 * - Used by Ordered Sentence Generator
 */
class WordAdderUpperReverse implements IWordAdder {
    public ArrayList<String> addWord(ArrayList<String> vocabulary, String word) {
        String wordUpper = word.toUpperCase();
        String wordReversed = new StringBuilder(wordUpper).reverse().toString();
        vocabulary.add(wordReversed);
        return vocabulary;
    }
}

/**
 * IWordGenerator
 */
interface IWordGenerator {
    public String generateWord(ArrayList<String> vocabulary);
}

/**
 * WordGeneratorRandom
 */
class WordGeneratorRandom implements IWordGenerator {

    @Override
    public String generateWord(ArrayList<String> vocabulary) {
        ArrayList<String> words = Randomizer.randomWordPicker(vocabulary);
        Collections.shuffle(words);
        return String.join(" ", words);
    }
}

/**
 * WordGeneratorSorted
 */
class WordGeneratorSorted implements IWordGenerator {

    @Override
    public String generateWord(ArrayList<String> vocabulary) {
        ArrayList<String> words = Randomizer.randomWordPicker(vocabulary);
        Collections.sort(words);
        return String.join(" ", words);
    }
}

/**
 * WordGeneratorOrdered
 */
class WordGeneratorOrdered implements IWordGenerator {

    @Override
    public String generateWord(ArrayList<String> vocabulary) {
        ArrayList<String> words = Randomizer.randomWordPicker(vocabulary);
        return String.join(" ", words);
    }
}

// Handler class for the main menu
class MenuHandler {
    private SentenceGenerator generator;
    private String generatorName;

    private Scanner scanner = new Scanner(System.in);

    public MenuHandler() {
        generator = null;
    }

    // Displays menu
    public boolean menu() {
        System.out.println("Select action: ");
        System.out.println("1. Add generator");
        System.out.println("2. Add word to vocabulary");
        System.out.println("3. Generate sentence");
        System.out.println("4. Print all words in vocaulary");
        System.out.println("5. Exit");

        // input choice
        String choiceStr = scanner.nextLine();
        int choice;
        try {
            choice = Integer.parseInt(choiceStr);
        } catch (NumberFormatException exp) {
            System.out.println("Invalid Input");
            return false;
        }

        switch (choice) {
            case 1:
                selectGenerator();
                return false;
            case 2:
                addToVocabulary();
                return false;
            case 3:
                generateSentence();
                return false;
            case 4:
                listWords();
                return false;
            case 5:
                return true;
            default:
                System.out.println("Invalid Input");
                return false;
        }
    }

    private SentenceGenerator createRSG() {
        return new SentenceGenerator(new WordAdderLower(), new WordGeneratorRandom());
    }

    private SentenceGenerator createSSG() {
        return new SentenceGenerator(new WordAdderLower(), new WordGeneratorSorted());
    }

    private SentenceGenerator createOSG() {
        return new SentenceGenerator(new WordAdderUpperReverse(), new WordGeneratorOrdered());
    }

    // add new generator
    public void selectGenerator() {
        if (generator != null) {
            System.out.printf("Generator already selected as %s\n", generatorName);
            return;
        }

        System.out.println("Select type of generator: ");
        System.out.println("1. Random Sentence Generator (RSG)");
        System.out.println("2. Sorted Sentence Generator (SSG)");
        System.out.println("3. Ordered Sentence Generator (OSG)");

        String choiceStr = scanner.nextLine();
        int choice;
        try {
            choice = Integer.parseInt(choiceStr);
        } catch (NumberFormatException exp) {
            System.out.println("Invalid Input");
            return;
        }

        String name = null;
        switch (choice) {
            case 1:
                name = "Random Sentence Generator";
                generator = createRSG();
                break;
            case 2:
                name = "Sorted Sentence Generator";
                generator = createSSG();
                break;
            case 3:
                name = "Ordered Sentence Generator";
                generator = createOSG();
                break;
            default:
                System.out.println("Invalid Input");
                break;
        }

        if (name != null && generator != null) {
            System.out.printf("Generator selected: %s\n", name);
            generatorName = name;
        }
    }

    // Add word to vocabulary
    public void addToVocabulary() {
        if (generator == null) {
            System.out.printf("No generator selected. Please select a generator first\n");
            return;
        }
        System.out.println("Please input a word");

        String wordToAdd = scanner.nextLine();
        generator.addWord(wordToAdd);
        System.out.printf("New word \"%s\" added to %s\n", wordToAdd, generatorName);
    }

    // Generate sentence with the preselected generator
    public void generateSentence() {
        if (generator == null) {
            System.out.printf("No generator selected. Please select a generator first\n");
            return;
        }

        String generatedSentence = generator.generateWord();
        System.out.printf("Generated sentence:%s\n", generatedSentence);
    }

    private void listWords() {
        if (generator == null) {
            System.out.printf("No generator selected. Please select a generator first\n");
            return;
        }

        System.out.printf("There are %s words in the vocabulary\n", Integer.toString(generator.vocabulary.size()));
        for (int i = 0; i < generator.vocabulary.size(); i++) {
            System.out.println(generator.vocabulary.get(i));
        }
    }
}

// Main driver class
public class SentenceGenerator10 {
    public static void main(String[] args) {
        MenuHandler handler = new MenuHandler();
        while (true) {
            boolean exit = handler.menu();
            if (exit)
                break;
            System.out.println("\n\n\n\n");
        }
    }
}
