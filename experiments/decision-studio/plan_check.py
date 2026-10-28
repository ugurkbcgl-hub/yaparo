"""Compact owned planning: real local browser, synthetic fields, no provider access."""

import unittest

from first_stage_check import FirstStageCheck


class PlanCheck(FirstStageCheck):
    def ready_paid(self):
        self.select_pair("promote", "visit")
        self.fill_remaining(mode="paid")
        self.submit()
        self.plan_basics()
        self.page.locator("#business").select_option("local_retail")
        self.page.locator("#sector").select_option("fashion_beauty_lifestyle")
        self.page.get_by_text(
            "ECB çapraz referans USD/TRY · Güncel kayıt", exact=True
        ).wait_for(state="attached")
        self.page.locator("#recommend").click()
        self.assertGreater(self.snapshot()["plan"]["allocated"], 0)

    def test_plan_no_invented_budget_location_or_repeated_audience(self):
        self.select_pair("promote", "visit")
        self.fill_remaining(mode="paid")
        self.submit()
        for field in ["budget", "region", "radius", "start", "plan-end", "geo-mode"]:
            self.assertEqual(self.page.locator(f"#{field}").input_value(), "")
        self.assertIn("Bireyler", self.page.locator("#plan-brief-summary").inner_text())
        self.assertIn(
            "Somut sentetik açıklama",
            self.page.locator("#plan-brief-summary").inner_text(),
        )
        self.assertTrue(self.page.locator("#audience").is_hidden())
        self.assertTrue(self.page.locator("#plan-radius-section").is_hidden())
        self.assertIsNone(self.snapshot()["plan"])
        for field in ["order-value", "margin", "cpa", "capacity"]:
            self.assertEqual(self.page.locator(f"#{field}").input_value(), "")
            self.assertTrue(self.page.locator(f"#{field}").is_disabled())
        self.page.locator("#recommend").click()
        self.assertIsNone(self.snapshot()["plan"])
        self.assertIn(
            "bölgesini seç", self.page.locator("#decision-status").inner_text()
        )

    def test_plan_same_pair_brief_edit_preserves_manual_bounds(self):
        self.ready_paid()
        self.page.locator('#step-nav [data-step="0"]').click()
        self.field("promote_name").fill("Sentetik güncel isim")
        self.submit()
        self.assertEqual(self.page.locator("#budget").input_value(), "3000")
        self.assertEqual(self.page.locator("#geo-mode").input_value(), "country")
        self.assertEqual(self.page.locator("#start").input_value(), "2026-11-01")
        self.assertEqual(self.page.locator("#plan-end").input_value(), "2026-11-07")

    def test_plan_percentages_selection_reserve_and_stale_guards(self):
        self.ready_paid()
        before = self.snapshot()["plan"]
        self.assertFalse(before["economicsProvided"])
        self.assertEqual(before["businessCap"], before["total"])
        selected = [row for row in before["rows"] if row["amount"]]
        self.assertGreaterEqual(len(selected), 2)
        channel = selected[0]["channel"]["id"]
        row = self.page.locator(f'#recommended [data-channel="{channel}"]')
        percent = row.locator('input[type="number"]')
        slider = row.locator('input[type="range"]')
        other_value = self.page.locator(
            '#recommended input[type="number"]'
        ).evaluate_all("nodes=>nodes.map(n=>n.value)")
        slider.scroll_into_view_if_needed()
        box = slider.bounding_box()
        current = float(slider.input_value()) / 100
        self.page.mouse.move(
            box["x"] + box["width"] * current, box["y"] + box["height"] / 2
        )
        self.page.mouse.down()
        self.page.mouse.move(
            box["x"] + box["width"] * 0.60, box["y"] + box["height"] / 2, steps=5
        )
        self.assertNotEqual(
            self.page.locator('#recommended input[type="number"]').evaluate_all(
                "nodes=>nodes.map(n=>n.value)"
            ),
            other_value,
        )
        self.page.mouse.up()
        self.assertTrue(self.snapshot()["plan"]["manual"])
        percent.fill("50")
        percent.dispatch_event("change")
        after = self.snapshot()["plan"]
        self.assertEqual(after["allocated"] + after["unallocated"], after["total"])
        self.assertNotEqual(
            [r["amount"] for r in before["rows"]],
            [r["amount"] for r in after["rows"]],
        )
        self.assertTrue(after["manual"])
        slider.evaluate(
            "el=>{el.value='0';el.dispatchEvent(new Event('input',{bubbles:true}));}"
        )
        self.assertEqual(percent.input_value(), "0.00")
        self.assertIn("0,00", row.locator(".compact-amount").inner_text())
        self.assertEqual(self.snapshot()["plan"]["allocated"], after["allocated"])
        slider.dispatch_event("pointercancel")
        row.locator('input[type="checkbox"]').click()
        removed = self.snapshot()["plan"]
        self.assertEqual(
            next(r for r in removed["rows"] if r["channel"]["id"] == channel)["amount"],
            0,
        )
        self.assertEqual(
            self.page.locator(f'#recommended [data-channel="{channel}"]').count(), 0
        )
        self.page.locator(".other-channels-box > summary").click()
        other = self.page.locator(f'#other-channels [data-channel="{channel}"]')
        self.assertEqual(other.locator('input[type="range"]').count(), 0)
        other.locator('input[type="checkbox"]').click()
        self.assertGreater(
            next(
                r
                for r in self.snapshot()["plan"]["rows"]
                if r["channel"]["id"] == channel
            )["amount"],
            0,
        )
        self.page.locator("#budget").fill("5000")
        self.assertTrue(self.snapshot()["stale"])
        self.assertIsNone(self.snapshot()["adaptations"])
        self.assertTrue(
            self.page.locator('#recommended input[type="number"]').first.is_disabled()
        )
        self.page.get_by_role("button", name="İçeriklere devam et").click()
        self.assertTrue(self.page.locator("#step-1").is_visible())

    def test_plan_radius_clips_turkey_and_refuses_invalid_centers(self):
        self.ready_paid()
        self.page.locator("#geo-mode").select_option("radius")
        self.assertTrue(self.page.locator("#plan-radius-section").is_visible())
        self.page.locator("#plan-coordinate-details > summary").click()
        self.page.locator("#plan-latitude").fill("41.005")
        self.page.locator("#plan-longitude").fill("29.04")
        self.page.locator("#radius").fill("80")
        result = self.page.evaluate(
            "YaparoPlanGeo.calculate({lat:41.005,lon:29.04,radius:80})"
        )
        self.assertTrue(result["valid"])
        self.assertLess(result["areaKm2"], result["rawAreaKm2"])
        self.assertIn("Türkiye içinde", self.page.locator("#plan-map").inner_text())
        self.page.evaluate("window.scrollTo(0,0)")
        self.page.screenshot(
            path=str(self.evidence / "compact-map-desktop.png"), full_page=True
        )
        self.assertTrue(self.snapshot()["stale"])
        self.page.locator("#recommend").click()
        self.assertEqual(self.snapshot()["plan"]["input"]["geoCenter"]["lat"], 41.005)
        self.assertEqual(self.snapshot()["plan"]["input"]["geo"], "radius_local")
        self.assertFalse(self.snapshot()["plan"]["publishable"])
        revision = self.snapshot()["revision"]
        self.page.locator("#plan-latitude").fill("48.8566")
        self.page.locator("#plan-longitude").fill("2.3522")
        self.page.locator("#recommend").click()
        self.assertEqual(self.snapshot()["revision"], revision)
        self.assertTrue(self.snapshot()["stale"])
        self.assertIn(
            "Türkiye içinde", self.page.locator("#decision-status").inner_text()
        )

    def test_plan_specific_dates_and_no_commerce_fields_for_donation(self):
        self.select_pair("sell", "purchase")
        self.fill_remaining(
            mode="paid",
            overrides={
                "sell_timing": "range",
                "sell_start": "2026-11-15",
                "sell_end": "2026-11-22",
            },
        )
        self.submit()
        self.assertEqual(self.page.locator("#start").input_value(), "2026-11-15")
        self.assertEqual(self.page.locator("#plan-end").input_value(), "2026-11-22")
        self.page.locator('#step-nav [data-step="0"]').click()
        self.select_pair("fundraise", "donate")
        self.fill_remaining(mode="paid")
        self.submit()
        self.assertTrue(self.page.locator(".economics").is_hidden())
        self.assertTrue(self.page.locator("#order-value").is_disabled())
        self.plan_basics()
        self.page.locator("#recommend").click()
        self.assertTrue(
            self.snapshot()["plan"] is None or self.snapshot()["plan"]["allocated"] == 0
        )

    def test_plan_visual_desktop_mobile_and_compact_review(self):
        self.ready_paid()
        self.page.locator("#plan-advanced > summary").click()
        self.page.evaluate("window.scrollTo(0,0)")
        self.page.screenshot(
            path=str(self.evidence / "compact-plan-desktop.png"), full_page=True
        )
        self.page.set_viewport_size({"width": 390, "height": 844})
        self.assertLessEqual(
            self.page.evaluate("document.documentElement.scrollWidth"), 390
        )
        self.page.evaluate("window.scrollTo(0,0)")
        self.page.screenshot(
            path=str(self.evidence / "compact-plan-mobile.png"), full_page=True
        )
        self.page.screenshot(
            path=str(self.evidence / "compact-plan-mobile-viewport.png")
        )
        footer = self.page.locator(".plan-footer button[type=submit]").bounding_box()
        helper = self.page.locator("#helper-toggle").bounding_box()
        self.assertTrue(
            helper["y"] + helper["height"] <= footer["y"]
            or helper["y"] >= footer["y"] + footer["height"]
        )
        self.page.get_by_role("button", name="İçeriklere devam et").click()
        self.page.locator(".choose").first.click()
        self.page.locator("#adapt-content").click()
        self.page.locator("#content-next").click()
        self.assertTrue(self.page.locator("#step-3").is_visible())
        self.assertEqual(
            self.page.locator("#review-all-answers").get_attribute("open"), None
        )
        self.assertIn("Başarı göstergesi", self.page.locator("#review").inner_text())
        self.page.evaluate("window.scrollTo(0,0)")
        self.page.screenshot(
            path=str(self.evidence / "compact-review-mobile.png"), full_page=True
        )
        self.assertLessEqual(
            self.page.evaluate("document.documentElement.scrollWidth"), 390
        )


def load_tests(loader, _tests, _pattern):
    # Reuse fixtures, not the whole first-stage suite (it runs separately in CI).
    return unittest.TestSuite(
        PlanCheck(name)
        for name in loader.getTestCaseNames(PlanCheck)
        if name.startswith("test_plan_")
    )


if __name__ == "__main__":
    unittest.main(verbosity=2)
