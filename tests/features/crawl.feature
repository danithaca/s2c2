Feature: simulate website crawl

  @javascript @dev
  Scenario: crawl family helper
    Given I am on "https://hr.umich.edu/benefits-wellness/family/work-life-resource-center/u-m-family-helpers/family-helper-profiles-disclaimer"
    And I follow "login"
    Then I should be on "https://weblogin.umich.edu/"
    When I fill in the following:
      | Login ID | mrzhou     |
      | Password | n4w%trh1xd |
    And I press "Log In"
    Then I should be on "https://hr.umich.edu/benefits-wellness/family/work-life-resource-center/u-m-family-helpers/family-helper-profiles-disclaimer"

    #When I check "I have read the disclaimer above and agree to its contents."
    #When I check "submitted[i_certify_the_following_to_be_true][agree]"
    #And I press "Submit"
    When I run the following Javascript:
      """
      jQuery('#edit-submitted-i-certify-the-following-to-be-true-1').click();
      jQuery('input.webform-submit[name="op"]').click();
      """
    And pause 3 seconds
    Then I should be on "https://hr.umich.edu/benefits-wellness/family/work-life-resource-center/u-m-family-helpers/family-helper-profiles"

    # this might take a long time.
    When I grab family helper data


#  @javascript
#  Scenario: test
#    Given I am on "http://localhost:63342/p2/logfiles/a.html"
#    When I grab family helper data