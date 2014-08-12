## Starting and checking the status of builds
There are three ways that builds start in our jenkins testing infastructure for edx-platform.  

##### 1) Automatic builds for Pull Requests
* How it gets started  
  
  >* When you submit a pull request to the edx-platform repository, a jenkins build will
  >  automatically start and run unit and acceptance tests at the most recent commit.
  >* When you add a new commit to the PR, a new build will be run for those changes.
  >* Sometimes it may take a little while for the build to start. That ussually just means that 
  >  jenkins is pretty busy.
  >* NOTE:  You must have the correct permissions on your github account for this to work. (i.e. Be
  >  a member of the edx organization on github or on a whitelist.)
  
* How it is reported  
  
  >* You will know a build is started if you see this:  
  >
  >  ![Running Tests](jenkins_images/started_tests.png)
  >
  >* When it is finished you will see either a green checkmark or a red X, indicating that the
  >  build either passed or failed respectively.  
  >
  >  ![Passed Tests](jenkins_images/passed_tests.png) 
  >
  >  ![Failed Tests](jenkins_images/failed_tests.png)  
  >* You can click on 'details' to take you to the jenkins build report.
    
##### 2) Manually started builds for pull requests
* How it gets started  
  
  >1. Go to [edx-all-tests-manual-pr](https://jenkins.testeng.edx.org/job/edx-all-tests-manual-pr/)
  >2. Make sure you are __logged in__.
  >3. Click 'Build with Parameters' in the left navigation column.
  >
  >  ![Build with Params](jenkins_images/build_w_params.png)
  >
  >4. Enter the PR number from edx-platform that you want to test.
  >5. Click on 'Build'.
  
* How it is reported  

  >* This will be reported the same as Automatic builds for Pull Requests are. (See point 1 of this
  >  section.)
  >* When you start the build, it will redirect you to the log page.  You can watch this page for
  >  results as well. 
  
##### 3) Manually started builds for commits
* How it gets started
  
  >1. Go to [edx-all-tests-manual-commit](https://jenkins.testeng.edx.org/job/edx-all-tests-manual-commit/)
  >2. Make sure you are __logged in__.
  >3. Click 'Build with Parameters' in the left navigation column.
  >4. Enter the commit hash that you want to test.
  >5. Click on 'Build'.
  
* How it is reported
  
  >* When you start the build, it will redirect you to the log page.  You can watch this page for
  >  results. 
  >* The results will also be reported to github, and will show up next to your commit on a PR or
  >  other places that the commit is listed (search results, etc.). 
