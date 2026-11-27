import json, sys, tempfile, unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import master  # noqa: E402

REG = master.load()
T0 = datetime(2026, 11, 27, 12, 0, 0, tzinfo=timezone.utc)


class Registry(unittest.TestCase):
    def test_validates(self):
        self.assertEqual(master.validate(REG), [])

    def test_every_active_repo_has_agent_file(self):
        for n, r in REG["repos"].items():
            if r["status"] in ("active", "vendored"):
                self.assertTrue((ROOT / ".claude/agents" / f"{r['agent']}.md").exists(), n)

    def test_agent_files_have_frontmatter(self):
        for a in REG["agents"]:
            txt = (ROOT / ".claude/agents" / f"{a}.md").read_text()
            self.assertTrue(txt.startswith(f"---\nname: {a}\ndescription: "), a)

    def test_validate_catches_bad_agent(self):
        bad = json.loads(json.dumps(REG))
        bad["repos"]["seo-desk"]["agent"] = "ghost"
        self.assertTrue(any("ghost" in e for e in master.validate(bad)))

    def test_validate_catches_bad_flow(self):
        bad = json.loads(json.dumps(REG))
        bad["flows"].append({"id": "x", "from": "nope", "to": "seo-desk", "via": "", "status": "proposed"})
        self.assertTrue(any("nope" in e for e in master.validate(bad)))


class Routing(unittest.TestCase):
    def top(self, text):
        return [r["repo"] for r in master.route(text, REG)]

    def test_seo(self):
        self.assertEqual(self.top("run a technical seo audit")[0], "seo-desk")

    def test_plural_stem(self):
        self.assertIn("reel-studio-kit", self.top("make faceless reels"))

    def test_pinterest(self):
        self.assertEqual(self.top("post a pinterest pin from a product url")[0], "pin-creator")

    def test_youtube(self):
        self.assertEqual(self.top("improve my youtube retention and chapters")[0], "youtube-agent-skill")

    def test_no_match(self):
        self.assertEqual(self.top("zzz qqq"), [])


class Handoffs(unittest.TestCase):
    def setUp(self):
        self.q = Path(tempfile.mkdtemp()) / "queue"

    def test_roundtrip(self):
        i = master.new_handoff(REG, "seo-liaison", "directory-liaison", "Fix titles!", "b", "x.md", self.q, T0)
        self.assertEqual(i["id"], "20261127T120000-directory-liaison-fix-titles")
        self.assertEqual(len(master.list_handoffs(self.q)), 1)
        self.assertEqual(master.list_handoffs(self.q, to="video-liaison"), [])
        done = master.close_handoff(i["id"], "ok", self.q, T0)
        self.assertEqual(done["status"], "done")
        self.assertEqual(master.list_handoffs(self.q), [])
        self.assertEqual(len(master.list_handoffs(self.q, status="all")), 1)

    def test_unknown_endpoint(self):
        with self.assertRaises(ValueError):
            master.new_handoff(REG, "seo-liaison", "ghost", "s", queue=self.q)

    def test_owner_allowed(self):
        master.new_handoff(REG, "release-gate", "owner", "approve?", queue=self.q, now=T0)

    def test_double_close_and_missing(self):
        i = master.new_handoff(REG, "master", "owner", "s", queue=self.q, now=T0)
        master.close_handoff(i["id"], queue=self.q)
        with self.assertRaises(ValueError):
            master.close_handoff(i["id"], queue=self.q)
        with self.assertRaises(ValueError):
            master.close_handoff("nope", queue=self.q)


class Cli(unittest.TestCase):
    def test_status_and_validate_exit_codes(self):
        self.assertEqual(master.main(["validate"]), 0)
        self.assertIn(master.main(["status"]), (0, 1))


if __name__ == "__main__":
    unittest.main()
