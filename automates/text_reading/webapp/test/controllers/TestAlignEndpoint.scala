package controllers

import com.typesafe.config.ConfigFactory
import org.scalatestplus.play._
import org.scalatestplus.play.guice._
import play.api.Application
import play.api.inject.guice.GuiceApplicationBuilder
import play.api.libs.json.Json
import play.api.mvc.Headers
import play.api.test._
import play.api.test.Helpers._

/**
  * Add your spec here.
  * You can mock out a whole application including requests, plugins etc.
  *
  * For more information, see https://www.playframework.com/documentation/latest/ScalaTestingWithScalaTest
  */
class TestAlignEndpoint extends PlaySpec with GuiceOneAppPerTest with Injecting {


  new GuiceApplicationBuilder()
    .build()
  val controller = new HomeController(stubControllerComponents())

  "align elements by accessing the /align endpoint" in {


    val body =
      Json.obj("pathToJson" -> """json={
        "pathToJson":"/home/alexeeva/Repos/automates/scripts/model_assembly/align_payload.json"}""")


    val result = route(
      app,
      FakeRequest(POST, "/align").withJsonBody(body).withHeaders(Headers(CONTENT_TYPE -> "application/json"))
    ).get//withJsonBody(Json.parse("""{ "field": "value" }"""))

    status(result) mustBe OK
    contentType(result) mustBe Some("application/json")
//    Helpers.contentAsString(result) must include("core")

  }


}
