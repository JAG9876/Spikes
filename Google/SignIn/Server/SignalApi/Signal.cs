using System.ComponentModel.DataAnnotations;

namespace SignalApi
{
    public class Signal
    {
        public DateTime Start { get; set; }

        public DateTime End { get; set; }

        public SignalTypeEnum Type { get; set; }

        public string Data { get; set; }
    }
}
