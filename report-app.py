import requests
import smtplib
import argparse
from email.message import EmailMessage
from datetime import datetime, timedelta, timezone

#Parse arguments and default parameters
parser = argparse.ArgumentParser(description='PR report')
parser.add_argument("-u", type=str, default="pytorch")
parser.add_argument("-r", type=str, default="torchtitan")
parser.add_argument("-e", type=str, default="eegs333@hotmail.com")

args = parser.parse_args()

user = args.u
repo = args.r
email = args.e

#Get PR list from a repository
def get_pr(api_url, user, repo):
    url = f"{api_url}/repos/{user}/{repo}/pulls"
    headers = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": "Bearer "
    }

    query_params = {
    "state": "all"
    }

    response = requests.get(url, headers=headers, params=query_params)

    if response.status_code == 200:
        pr_data = response.json()
        response.close()
        return pr_data
    else:
        return None

#Get merge status from a PR number
def get_merge_status(api_url, user, repo, pr_number):
    url = f"{api_url}/repos/{user}/{repo}/pulls/{pr_number}/merge"
    headers = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": "Bearer "

    }

    response = requests.get(url, headers=headers)
    merge_code = response.status_code
    response.close()

    return merge_code

#Send mail with the html report
def send_mail(to_email, repo_name, msg_report ):
    EMAIL_ADDRESS = 'eegs333@gmail.com'
    EMAIL_PASSWORD = ''

    msg = EmailMessage()
    msg['Subject'] = 'Weekly report of PRs from the ' + repo_name + ' repository'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg.set_content('''
        <!-- index.html -->
        <!DOCTYPE html>
        <html>

        <head>
            <style>
            table,
            th,
            td {
                border: 1px solid black;
                border-collapse: collapse;
            }
            th,
            td {
              padding: 10px;
            }
            th {
              text-align: left;
            }
            </style>
        </head>

        <body >
            <h3>Weekly report of PRs from the ''' + repo_name + ''' repository</h3>
            <table>
              <tr>
                <th>#</th>
                <th>Date</th>
                <th>Title</th>
                <th>Branch</th>
                <th>State</th>
                <th>Merged</th>
              </tr>
              ''' + msg_report + '''

            </table>
        </body>
        </html>

    ''', subtype='html')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)
        print("Report sent...")


def main():
    api_url = "https://api.github.com"
    html_out = ""
    pr_list = get_pr(api_url, user, repo)
    date_now = datetime.now(timezone.utc).replace(microsecond=0)
    if pr_list:
        print("Listing PRs...")
        for pr in pr_list:
            date_from_pr = datetime.strptime(pr["created_at"], '%Y-%m-%dT%H:%M:%S%z')
            if date_now - timedelta(weeks=1) < date_from_pr:
                html_out +=  "<tr> <td>{}</td> <td>{}</td> <td>{}</td> <td>{}</td> <td>{}</td> <td>{}</td>  </tr>".format(pr["number"],
                pr["created_at"],
                pr["title"],
                pr["base"]["ref"],
                pr["state"],
                "Merged" if get_merge_status(api_url, user, repo, pr["number"]) == 204 else "Not merged")+"\n"
        send_mail(email, repo, html_out)
    else:
        print("PRs don't found...")

if __name__ == "__main__":
    main()
