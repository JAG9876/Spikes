using System.Text.Json;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Authentication.OpenIdConnect;

namespace WebApp
{
    public class Program
    {
        public static void Main(string[] args)
        {
            var builder = WebApplication.CreateBuilder(args);

            builder.Services
                .AddAuthentication(options => {
                        options.DefaultScheme = CookieAuthenticationDefaults.AuthenticationScheme;
                        options.DefaultChallengeScheme = OpenIdConnectDefaults.AuthenticationScheme;
                    })
                .AddCookie()
                .AddOpenIdConnect(options => {
                        options.Authority = builder.Configuration["OidcTest:Authority"];
                        options.ClientId = builder.Configuration["OidcTest:ClientId"];
                        options.ClientSecret = builder.Configuration["OidcTest:ClientSecret"];

                        options.ResponseType = "code";
                        options.SaveTokens = true;
                        options.CallbackPath = builder.Configuration["OidcTest:CallbackPath"];

                        options.Scope.Clear();
                        options.Scope.Add("openid");
                        options.Scope.Add("profile");
                        options.Scope.Add("email");

                        options.Events = new OpenIdConnectEvents
                        {
                            OnRemoteFailure = context =>
                            {
                                context.HandleResponse();
                                context.Response.Redirect("/Error?message=" + Uri.EscapeDataString(context.Failure?.Message ?? "Unknown error"));
                                return Task.CompletedTask;
                            },
                            OnTokenValidated = context =>
                            {
                                var principal = context.Principal;
                                var identity = principal?.Identity as System.Security.Claims.ClaimsIdentity;

                                // You can add custom claims or perform additional validation here
                                return Task.CompletedTask;
                            },
                            OnAuthenticationFailed = context =>
                            {
                                context.HandleResponse();
                                context.Response.StatusCode = 500;
                                context.Response.ContentType = "text/plain";
                                return context.Response.WriteAsync("An error occurred processing your authentication.");
                            }
                        };
                    });

            // Add services to the container.
            builder.Services.AddControllersWithViews();

            var app = builder.Build();

            // Configure the HTTP request pipeline.
            if (!app.Environment.IsDevelopment())
            {
                app.UseExceptionHandler("/Home/Error");
                // The default HSTS value is 30 days. You may want to change this for production scenarios, see https://aka.ms/aspnetcore-hsts.
                app.UseHsts();
            }

            app.UseHttpsRedirection();
            app.UseStaticFiles();

            app.UseRouting();

            app.UseAuthentication();
            app.UseAuthorization();

            app.MapControllerRoute(
                name: "default",
                pattern: "{controller=Home}/{action=Index}/{id?}");

            app.Run();
        }
    }
}
