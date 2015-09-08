Feature: test users interactions between the client and the server

  # todo: this should be on the "@core" level, but we don't have a good way to open email now.

  @javascript
  Scenario: match response
    Given I am logged in as user "test1@servuno.com" with password "password"
    When I open the last email from "test@servuno.com" to "test1@servuno.com"
    When I follow the email link like "/contract/match/"
    Then the URL should match "/contract/match/\d+/"
    And I should see "John Smith"
    And I should see "Your response?"

    # first, try decline.
    When I fill in "match-response" with "message-i-declined"
    When I press "Decline"
    Then I should see "Declined"
    And I should see a "button[name='edit']" element
    # And I should not see a "button[name='match']" element
    When I evaluate the following Javascript:
      """
      return $("button[name='match']").is(':hidden');
      """
    Then check Javascript result is true

    And the "match-response" field should contain "message-i-declined"
    When I evaluate the following Javascript:
      """
      return $('#match-response').attr('readonly') == 'readonly';
      """
    Then check Javascript result is true

    # check edit button
    When I press "Edit"
    And I should see "Accept"
    #And I should not see an "button[name='edit']" element
    When I evaluate the following Javascript:
      """
      return $("button[name='edit']").is(':hidden');
      """
    Then check Javascript result is true

    When I evaluate the following Javascript:
      """
      return $('#match-response').attr('readonly') != 'readonly';
      """
    Then check Javascript result is true

    # next, accept
    When I fill in "match-response" with "message-i-accepted-extra"
    When I press "Accept"
    Then I should see "Accepted"
    And the "match-response" field should contain "message-i-accepted-extra"

    When I press "Edit"
    When I fill in "match-response" with "message-i-accepted"
    When I press "Accept"
    Then I should see "Accepted"
    And the "match-response" field should contain "message-i-accepted"
    And the "match-response" field should not contain "message-i-accepted-extra"


  Scenario: check email
    When I open the last email
    Then check email sent from "test1@servuno.com" to "test@servuno.com"
    And check email subject contains "accepted your request"
    And check email contains "Review and confirm here"

  @javascript
  Scenario: edit contract, without submit
    Given I am logged in as user "test@servuno.com" with password "password"
    When I open the last email
    Then check email sent from "test1@servuno.com" to "test@servuno.com"
    When I follow the email link like "/contract/"
    Then the URL should match "/contract/\d+/"

    When I follow "Edit"
    Then the URL should match "/contract/\d+/edit/"
    When I evaluate the following Javascript:
      """
      return $('#id_event_start').attr('readonly') == 'readonly' && $('#id_event_end').attr('readonly') == 'readonly';
      """
    Then check Javascript result is true


  @javascript
  Scenario: confirm contract
    Given I am logged in as user "test@servuno.com" with password "password"
    When I open the last email from "test1@servuno.com" to "test@servuno.com"
    When I follow the email link like "/contract/"
    Then the URL should match "/contract/\d+/"

    Then I should see a "div[data-slug='test1-bot']" element
    And I should see a "div[data-slug='test1-bot'] button.btn-success" element
    And I should see "message-i-accepted"

    When I run the following Javascript:
      """
      $('div[data-slug="test1-bot"] button.btn-success').click();
      """
    Then pause 1 second
    When I run the following Javascript:
      """
      $('button[data-bb-handler="confirm"]').click();
      """
    Then pause 1 second
    Then I should see "Active - Confirmed"
    And I should see a "div[data-slug='test1-bot'] .label-success" element
    And I should see "Expired"
    And I should see "Undo"


  Scenario: check confirmation email
    # give some time for celery to catch up.
    Then pause 10 seconds
    When I open the last email from "test@servuno.com" to "test1@servuno.com"
    Then check email subject contains "John Smith confirmed your offer"
    And check email contains "John Smith confirmed your offer of help. Details of the request"
    And check email contains "Please contact John directly if you need to change, cancel, or ask for more information. You can response to the email directly or use the following information"

    When I open the last email from "test1@servuno.com" to "test@servuno.com"
    Then check email subject contains "Confirmation"
    And check email contains "You have confirmed the offer from Test1 Bot."


  @javascript
  Scenario: undo and cancel
    Given I am logged in as user "test@servuno.com" with password "password"
    When I open the last email from "test1@servuno.com" to "test@servuno.com"
    When I follow the email link like "/contract/"
    Then the URL should match "/contract/\d+/"

    When I press "Undo"
    Then pause 1 second
    When I run the following Javascript:
      """
      $('button[data-bb-handler="confirm"]').click();
      """
    Then I should see "Cancel"

    # check email
    When I open the last email from "test@servuno.com" to "test1@servuno.com"
    Then check email subject contains "John Smith canceled your confirmed offer"

    When I press "Cancel"
    When I run the following Javascript:
      """
      $('button[data-bb-handler="confirm"]').click();
      """
    Then I should see "Canceled"

    When I open the last email from "test@servuno.com" to "test1@servuno.com"
    Then check email subject contains "Request canceled"