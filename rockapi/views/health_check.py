from django.http import JsonResponse
import requests


def health_check(request):
    return JsonResponse({
        "status": "ok",
        "instance": get_instance_id()
    })


def get_instance_id():
    try:
        token = requests.put(
            "http://169.254.169.254/latest/api/token",
            headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"},
            timeout=0.2
        ).text

        resp = requests.get(
            "http://169.254.169.254/latest/meta-data/instance-id",
            headers={"X-aws-ec2-metadata-token": token},
            timeout=0.2
        )

        return resp.text
    except Exception as e:
        return "unknown"
