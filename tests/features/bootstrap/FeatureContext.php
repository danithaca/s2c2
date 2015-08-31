<?php

use Behat\Behat\Context\Context;
use Behat\Behat\Context\SnippetAcceptingContext;
use Behat\Behat\Hook\Scope\AfterStepScope;
use Behat\Gherkin\Node\PyStringNode;
use Behat\Gherkin\Node\TableNode;
use Behat\Mink\Exception\UnsupportedDriverActionException;
use Behat\MinkExtension\Context\MinkContext;
use Behat\Testwork\Hook\Scope\BeforeSuiteScope;

/**
 * Defines application features from the specific context.
 */
class FeatureContext extends MinkContext implements SnippetAcceptingContext
{

  protected $emailsPath;
  protected $screenshotsPath;
  protected $disableEmails = FALSE;
  protected $currentEmailFileName;
  protected $javascriptResult;

  static protected $sessionTimestamp;
  static protected $suite;

  /**
   * @BeforeSuite
   */
  public static function prepare(BeforeSuiteScope $scope) {
    self::$sessionTimestamp = time();
    self::$suite = $scope->getSuite();
  }

  /**
   * Initializes context.
   *
   * Every scenario gets its own context instance.
   * You can also pass arbitrary arguments to the
   * context constructor through behat.yml.
   */
  public function __construct()
  {
    $logfiles_path = self::$suite->hasSetting('logfiles_path') ? self::$suite->getSetting('logfiles_path') : '.';
    $this->emailsPath = $logfiles_path . DIRECTORY_SEPARATOR . 'emails';
    $this->screenshotsPath = $logfiles_path . DIRECTORY_SEPARATOR . 'screenshots';
    if (self::$suite->hasSetting('disable_emails')) {
      $this->disableEmails = @self::$suite->getSetting('disable_emails');
    }
  }

  /**
   * @When I open the recent email: :index
   */
  public function navigateRecentEmail($index)
  {
    $files = scandir($this->emailsPath , SCANDIR_SORT_DESCENDING);
    if ($files && isset($files[$index - 1])) {
      $this->currentEmailFileName = $files[$index - 1];
    } else {
      throw new Exception("Email not found at index: $index");
    }
  }

  /**
   * @When I open the last email
   */
  public function navigateLatestEmail()
  {
    return $this->navigateRecentEmail(1);
  }

  /**
   * @When I open the last email from :from_email to :to_email
   */
  public function navigateLatestEmailAddress($from_email, $to_email)
  {
    $i = 0;
    while (TRUE) {
      $i++;
      try {
        $this->navigateRecentEmail($i);
        try {
          $this->checkEmailAddress($from_email, $to_email);
          // found the email. break here.
          break;
        } catch (Exception $e) {
          // do nothing, this is not the right email.
        }
      } catch (Exception $e) {
        throw new Exception("Cannot find the latest email from $from_email to $to_email");
        // break;
      }
    }
  }

  protected function readCurrentEmail() {
    if ($this->currentEmailFileName)
      return file_get_contents($this->emailsPath . DIRECTORY_SEPARATOR . $this->currentEmailFileName);
    else
      throw new Exception("Email not set.");
  }

  protected function parseCurrentEmail() {
    if (!$this->currentEmailFileName || !($handle = @fopen($this->emailsPath . DIRECTORY_SEPARATOR . $this->currentEmailFileName, "r")))
      throw new Exception('Email not set, or cannot read email.');

    $result = array();

    while (($buffer = fgets($handle)) !== false) {
      if (strpos($buffer, 'From: ') === 0) {
        $result['from'] = trim(substr($buffer, 6));
      }
      else if (strpos($buffer, 'Reply-To: ') === 0) {
        $result['reply-to'] = trim(substr($buffer, 10));
      }
      else if (strpos($buffer, 'To: ') === 0) {
        $result['to'] = trim(substr($buffer, 4));
      }
      else if (strpos($buffer, 'Subject: ') === 0) {
        $result['subject'] = trim(substr($buffer, 9));
      }
      else if (strlen(trim($buffer)) === 0) {
        $body = '';
        while (($line = fgets($handle)) !== FALSE) {
          if (strpos($line, '----------') === 0) {
            break;
          }
          $body .= $line;
        }
        $result['body'] = $body;
      }
    }

    if (!feof($handle)) {
        throw new Exception('Email file reading error.');
    }
    @fclose($handle);

    return $result;
  }

  /**
   * Pauses the scenario until the user presses a key. Useful when debugging a scenario.
   *
   * @Then (I )break
  */
  public function breakPoint()
  {
    fwrite(STDOUT, "\033[s \033[93m[Breakpoint] Press \033[1;93m[RETURN]\033[0;93m to continue...\033[0m");
    while (fgets(STDIN, 1024) == '') {}
    fwrite(STDOUT, "\033[u");
    return;
  }

  /**
   * @Then show email content
   */
  public function showEmailContent()
  {
    echo $this->readCurrentEmail();
  }

  /**
   * @Then show email parsed content
   */
  public function showEmailParsedContent()
  {
    print_r($this->parseCurrentEmail());
  }

  /**
   * @Then check email sent from :from_email to :to_email
   */
  public function checkEmailAddress($from_email, $to_email)
  {
      $email = $this->parseCurrentEmail();
      if ((stripos(@$email['from'], $from_email) === FALSE && stripos(@$email['reply-to'], $from_email) === FALSE) || stripos(@$email['to'], $to_email) === FALSE) {
        throw new Exception("Expected emails and actual emails do not match. In file '{$this->currentEmailFileName}': {$email['from']} (from), {$email['reply-to']} (reply-to), {$email['to']} (to).");
      }
  }

  /**
   * @Then check email sent to :to_email
   */
  public function checkEmailTo($to_email)
  {
      $email = $this->parseCurrentEmail();
      if (stripos(@$email['to'], $to_email) === FALSE) {
        throw new Exception("Expected email '{$to_email}' and actual email '{$email['to']}' do not match. In file '{$this->currentEmailFileName}");
      }
  }

  /**
   * @Then check email contains :text
   */
  public function checkEmailText($text)
  {
    $email = $this->parseCurrentEmail();
    if (stripos(@$email['body'], $text) === FALSE) {
      throw new Exception("Cannot find text in email file '{$this->currentEmailFileName}'");
    }
  }

  /**
   * @Then check email subject contains :text
   */
  public function checkEmailSubject($text)
  {
    $email = $this->parseCurrentEmail();
    if (stripos(@$email['subject'], $text) === FALSE) {
      throw new Exception("Cannot find subject text in email file '{$this->currentEmailFileName}'");
    }
  }

  /**
   * @When I follow the email link like :link_pattern
   */
  public function followEmailLink($link_pattern)
  {
      $email = $this->parseCurrentEmail();
      $fn = $this->currentEmailFileName;
      if (!@$email['body']) {
        throw new Exception("Cannot parse email body in '$fn''.");
      }

      $search = preg_quote($link_pattern, '/');
      $matches = array();
      $found = preg_match('/\s(\S*'. $search .'\S*)\s/i', $email['body'], $matches);

      if (!$found || !($url = @$matches[1])) {
        throw new Exception("Cannot find the expected link pattern in '$fn''.");
      }

      echo "Follow link: $url";
      $this->visit($url);
  }

  /**
   * @Given I am logged in as user :user with password :password
   */
  public function loginAsUser($user, $password) {
    $this->getSession()->visit($this->locatePath('/account/login'));
    $element = $this->getSession()->getPage();
    $element->fillField('Email', $user);
    $element->fillField('Password', $password);
    $submit = $element->findButton('Log in');
    $submit->click();

    try {
      $this->assertResponseContains("<!-- logged in as $user -->");
    } catch (\Exception $e) {
      throw new \Exception("Failed to log in as user '$user' with password '$password'");
    }
  }

  /**
   * @Given I am logged in as admin
   */
  public function loginAsAdmin() {
    $this->getSession()->visit($this->locatePath('/admin/login'));
    $element = $this->getSession()->getPage();
    $element->fillField('Username', 'admin');
    $element->fillField('Password', '0623451');
    $submit = $element->findButton('Log in');
    $submit->click();

    try {
      $this->assertResponseContains("Django administration");
    } catch (\Exception $e) {
      throw new \Exception("Failed to log in as admin.");
    }
  }

  protected function _saveFile($raw_filename, $content) {
    $raw_filename = $raw_filename ?: sprintf('%s_%s.%s', date('c'), uniqid('', true), 'png');
    if ($this->screenshotsPath && !file_exists($this->screenshotsPath)) {
      mkdir($this->screenshotsPath);
    }
    $raw_pathname = $this->screenshotsPath . DIRECTORY_SEPARATOR . date('Y-m-d') . '-' . self::$sessionTimestamp;
    if (!file_exists($raw_pathname)) {
      mkdir($raw_pathname);
    }
    $filename = $raw_pathname . DIRECTORY_SEPARATOR . $raw_filename;
    file_put_contents($filename, $content);
  }

  /**
   * @Then /^take a screenshot$/
   */
  public function takeScreenshot($raw_filename = null) {
    $raw_filename = $raw_filename ?: sprintf('%s_%s_%s.%s', $this->getMinkParameter('browser_name'), date('c'), uniqid('', true), 'png');
    $this->_saveFile($raw_filename, $this->getSession()->getScreenshot());
  }

  /**
   * @Then /^save last response$/
   */
  public function savePage($raw_filename = null) {
    $raw_filename = $raw_filename ?: sprintf('page_%s_%s.%s', date('c'), uniqid('', true), 'html');
    $this->_saveFile($raw_filename, $this->getSession()->getPage()->getContent());
  }

  /**
   * @AfterStep
   */
  public function takeScreenshotAfterFailedStep(AfterStepScope $scope)
  {
    if (99 === $scope->getTestResult()->getResultCode()) {
      $raw_filename_prefix = sprintf('%s_%s_%d_%s', date('His'), preg_replace('/\W+/', '', $scope->getFeature()->getTitle()), $scope->getStep()->getLine(), preg_replace('/\W+/', '', $scope->getStep()->getText()));
      try {
        $raw_filename = sprintf('%s_%s.png', $raw_filename_prefix, $this->getMinkParameter('browser_name'));
        $this->takeScreenshot($raw_filename);
      } catch(UnsupportedDriverActionException $e) {
        $raw_filename = sprintf('%s_page.html', $raw_filename_prefix);
        $this->savePage($raw_filename);
      }
//      $step = $scope->getStep();
//      $step->screenshotUrl = date('Y-m-d') . '-' . self::$sessionTimestamp . '/' . $raw_filename;
    }
  }

  /**
   * @Then print the setting :key
   */
  public function printSetting($key)
  {
    if (self::$suite->hasSetting($key)) {
      print_r(self::$suite->getSetting($key));
    }
    else {
      echo "Key '$key' not found in settings.";
    }
  }

  /**
   * @Then /^pause (?P<seconds>\d+) second(s?)$/
   */
  public function pauseSeconds($seconds)
  {
    sleep($seconds);
  }

  /**
   * @When I run the following Javascript:
   */
  public function runLongJavascript(PyStringNode $jsBlock)
  {
    // $this->getSession()->executeScript() only execute a single line of code.
    // we'll preprocess it to allow multiple lines of execution
    $js = $jsBlock->getRaw();
    $js = "(function () {\n  $js  \n})();";
    $this->getSession()->executeScript($js);

    // wait 1 second for selenium to catch up on the browser side.
    $this->pauseSeconds(1);
    $this->getSession()->wait(500, 'false');
  }

  /**
   * @When I evaluate the following Javascript:
   */
  public function evaluateLongJavascript(PyStringNode $jsBlock)
  {
    // $this->getSession()->executeScript() only execute a single line of code.
    // we'll preprocess it to allow multiple lines of execution
    $js = $jsBlock->getRaw();
    $this->javascriptResult = $this->getSession()->evaluateScript($js);
  }

  /**
   * @Then check Javascript result is true
   */
  public function checkJavascriptResultBoolean()
  {
    if (!$this->javascriptResult) {
      throw new Exception("Javascript is not true.");
    }
  }

  /**
   * @Transform /^:([A-Z_]+)$/
   */
  public function constantMapping($key)
  {
    $mapping = array(
      'SIGNUP_LANDING' => '/account/onboard/about/',
      'LOGIN_LANDING' => '/dashboard/',
      'MANAGE_CONTACTS_DEFAULT' => '/circle/manage/personal/',
    );
    return @$mapping[$key];
  }

  /**
   * @Then the :element element is hidden
   */
  public function checkElementHidden($element)
  {
    $js = "return $('{$element}').is(':hidden');";
    if (!$this->getSession()->evaluateScript($js)) {
      throw new Exception("Element {$element} is not hidden.");
    }
  }
}
