using Google.Apis.Auth;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace SignalApi.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    //[Authorize]
    public class SignalsController : ControllerBase
    {
        [HttpPost("confirmIdentity")]
        public async Task<IActionResult> ConfirmIdentity(string idToken)
        {
            var Payload = await GoogleJsonWebSignature.ValidateAsync(idToken);
            var result = Ok(new { Message = "Identity confirmed" });

            return result;
        }


        [HttpPost("wav")]
        public IActionResult AddWavs(IEnumerable<Signal> signals)
        {
            return Ok(new { Message = "Wavs received", Count = signals.Count() });
        }
    }
}
