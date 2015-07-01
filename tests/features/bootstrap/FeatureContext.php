<?php

use Behat\Behat\Context\Context;
use Behat\Behat\Context\SnippetAcceptingContext;
use Behat\Gherkin\Node\PyStringNode;
use Behat\Gherkin\Node\TableNode;
use Behat\MinkExtension\Context\MinkContext;

/**
 * Defines application features from the specific context.
 */
class FeatureContext extends MinkContext implements SnippetAcceptingContext
{

  protected $email_path;

  /**
   * Initializes context.
   *
   * Every scenario gets its own context instance.
   * You can also pass arbitrary arguments to the
   * context constructor through behat.yml.
   */
  public function __construct($email_path)
  {
    $this->email_path = $email_path;
  }

  protected function getLastEmailFilename() {
    $files = scandir($this->email_path , SCANDIR_SORT_DESCENDING);
    if ($files) {
      return $files[0];
    } else {
      return FALSE;
    }
  }

  protected function readLastEmail() {
    if ($fn = $this->getLastEmailFilename())
      return file_get_contents($this->email_path . DIRECTORY_SEPARATOR . $fn);
    else
      return FALSE;
  }

  protected function parseLastEmail() {
    $fn = $this->getLastEmailFilename();
    if (!$fn || !($handle = @fopen($this->email_path . DIRECTORY_SEPARATOR . $fn, "r"))) return FALSE;

    $result = array();

    while (($buffer = fgets($handle)) !== false) {
      if (strpos($buffer, 'From: ') === 0) {
        $result['from'] = trim(substr($buffer, 6));
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
  public function iPutABreakpoint()
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
    $content = $this->readLastEmail();
    if ($content) {
      echo $content;
    } else {
      echo 'No email found.';
    }
  }

  /**
   * @Then show email parsed content
   */
  public function showEmailParsedContent()
  {
    $content = $this->parseLastEmail();
    if ($content) {
      print_r($content);
    } else {
      echo 'No email found.';
    }
  }

  /**
   * @Then check email sent from :from_email to :to_email
   */
  public function checkEmailAddress($from_email, $to_email)
  {
      $email = $this->parseLastEmail();
      if ($from_email != @$email['from'] || $to_email != @$email['to']) {
        $fn = $this->getLastEmailFilename();
        throw new Exception("Expected emails and actual emails do not match. In file '{$fn}': {$email['from']} (from), {$email['to']} (to).");
      }
  }

  /**
   * @Then check email contains :text
   */
  public function checkEmailText($text)
  {
    $email = $this->parseLastEmail();
    if (stripos(@$email['body'], $text) === FALSE) {
      $fn = $this->getLastEmailFilename();
      throw new Exception("Cannot find text in email file '{$fn}'");
    }
  }

  /**
   * @Then check email subject contains :text
   */
  public function checkEmailSubject($text)
  {
    $email = $this->parseLastEmail();
    if (stripos(@$email['subject'], $text) === FALSE) {
      $fn = $this->getLastEmailFilename();
      throw new Exception("Cannot find subject text in email file '{$fn}'");
    }
  }

  /**
   * @When I follow the email link like :link_pattern
   */
  public function followEmailLink($link_pattern)
  {
      $email = $this->parseLastEmail();
      $fn = $this->getLastEmailFilename();
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

}
